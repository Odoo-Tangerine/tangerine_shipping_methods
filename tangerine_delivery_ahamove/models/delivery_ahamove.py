# -*- coding: utf-8 
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_base.settings import utils
from ..settings.constants import settings
from ..api.connection import Connection
from ..api.client import Client


class ProviderAhamove(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('ahamove', 'Ahamove')
    ], ondelete={'ahamove': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    ahamove_api_key = fields.Char(string='API Key')
    ahamove_partner_name = fields.Char(string='Name')
    ahamove_partner_phone = fields.Char(string='Phone')
    ahamove_refresh_token = fields.Char(string='Refresh Token')
    ahamove_service_request_domain = fields.Binary(default=[], store=False)
    default_ahamove_service_id = fields.Many2one('ahamove.service', string='Service Type')
    default_ahamove_service_request_ids = fields.Many2many(
        'ahamove.service.request',
        'delivery_request_rel',
        'delivery_id',
        'request_id',
        string='Request Type'
    )
    default_ahamove_payment_method = fields.Selection(selection=settings.payment_method.value, string='Payment Method')

    @api.onchange('default_ahamove_service_id')
    def _onchange_default_ahamove_service_id(self):
        for rec in self:
            if rec.default_ahamove_service_id:
                rec.ahamove_service_request_domain = [('service_id', '=', rec.default_ahamove_service_id.id)]

    def ahamove_get_access_token(self):
        try:
            if not self.ahamove_partner_phone:
                raise UserError(_('The field phone is required'))
            elif not self.ahamove_api_key:
                raise UserError(_('The field API key is required'))
            client = Client(Connection(self))
            route_id = utils.get_route_api(self, settings.get_token_route_code.value)
            result = client.get_access_token(route_id)
            self.write({
                'access_token': result.get('token'),
                'ahamove_refresh_token': result.get('refresh_token')
            })
            return utils.notification('success', 'Get access token successfully')
        except Exception as e:
            raise UserError(_(ustr(e)))

    def ahamove_rate_shipment(self, order):
        client = Client(Connection(self))
        route_id = utils.get_route_api(self, settings.estimate_order_route_code.value)
        result = client.estimate_order_fee(route_id, order)
        return {
            'success': True,
            'price': result.get('total_price'),
            'error_message': False,
            'warning_message': False
        }

    def ahamove_send_shipping(self, pickings):
        client = Client(Connection(self))
        route_id = utils.get_route_api(self, settings.create_order_route_code.value)
        for picking in pickings:
            result = client.create_order(route_id, picking)
            return [{
                'exact_price': result.get('order').get('total_price'),
                'tracking_number': result.get('order_id')
            }]

    def ahamove_cancel_shipment(self, picking):
        if picking.status_id.code not in settings.list_status_cancellation_allowed.value:
            raise UserError(_(f'You cannot cancel while the order is in {picking.status_id.name} status'))
        client = Client(Connection(self))
        route_id = utils.get_route_api(self, settings.cancel_order_route_code.value)
        client.cancel_order(route_id, picking.carrier_tracking_ref)
        picking.write({
            'carrier_tracking_ref': False,
            'carrier_price': 0.0
        })
        return utils.notification(
            'success',
            f'Cancel tracking reference {picking.carrier_tracking_ref} successfully'
        )

    def ahamove_toggle_prod_environment(self):
        self.ensure_one()
        if self.prod_environment:
            self.domain = settings.domain_production.value
        else:
            self.domain = settings.domain_staging.value

    @staticmethod
    def ahamove_get_tracking_link(picking):
        route = f'/share-order/{picking.carrier_tracking_ref}/{picking.carrier_id.ahamove_partner_phone}'
        if picking.prod_enviroment:
            return f'{settings.tracking_url_production.value}{route}'
        return f'{settings.tracking_url_staging.value}{route}'
