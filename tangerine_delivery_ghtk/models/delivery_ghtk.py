# -*- coding: utf-8
import time
import math
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_base.settings.utils import standardization_e164, get_route_api, notification
from odoo.addons.tangerine_delivery_base.api.connection import Connection
from ..settings.constants import settings
from ..api.client import Client


class ProviderAhamove(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('ghtk', 'GHTK')
    ], ondelete={'ghtk': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    default_ghtk_pick_shift = fields.Selection(settings.pick_shift.value, string='Pick Shift')
    default_ghtk_payer_type = fields.Selection(settings.payer_type.value, string='Payer')
    default_ghtk_transport_type = fields.Selection(settings.transport_type.value, string='Transport Type')
    default_ghtk_service_type = fields.Selection(settings.service_type.value, string='Service Type')
    default_ghtk_special_service_type_ids = fields.Many2many('ghtk.special.service', string='Special Service Type')
    default_ghtk_print_layout = fields.Selection(settings.print_layouts.value, string='Print Layout')
    default_ghtk_paper_size = fields.Selection(settings.paper_size.value, string='Paper Size')

    def _ghtk_payload_estimate_order(self, order):
        warehouse_id = order.warehouse_id
        if not warehouse_id:
            raise UserError(_('The warehouse is required on sale order'))
        payload = {
            'pick_province': warehouse_id.partner_id.state_id.name,
            'pick_district': warehouse_id.partner_id.district_id.name,
            'pick_ward': warehouse_id.partner_id.ward_id.name,
            'pick_street': warehouse_id.partner_id.street,
            'province': order.partner_shipping_id.state_id.name,
            'district': order.partner_shipping_id.district_id.name,
            'ward': order.partner_shipping_id.ward_id.name,
            'address': order.partner_shipping_id.street,
            'weight': math.ceil(self.convert_weight(order._get_estimated_weight(), self.base_weight_unit)),
            'value': order.amount_total,
            'transport': order.env.context.get('ghtk_transport_type', 'road'),
            'deliver_option': 'xteam',
        }
        if order.env.context.get('ghtk_special_service_type', []):
            payload['tags[]'] = order.env.context.get('ghtk_special_service_type')
        if order.env.context.get('ghtk_service_type', 'standard') == 'standard':
            del payload['deliver_option']
        return payload

    def ghtk_rate_shipment(self, order):
        client = Client(Connection(self, get_route_api(self, settings.ghtk_estimate_order_route_code.value)))
        result = client.estimate_order(self._ghtk_payload_estimate_order(order))
        return {
            'success': True,
            'price': result.get('fee').get('fee'),
            'error_message': False,
            'warning_message': False
        }

    def _ghtk_payload_create_order(self, picking, data):
        sender_id = picking.picking_type_id.warehouse_id.partner_id
        payload = {
            'order': {
                'id': str(int(time.time() * 1e6)),
                'pick_money': math.ceil(picking.cash_on_delivery_amount) if picking.cash_on_delivery else 0,
                'pick_name': sender_id.name,
                'pick_address': sender_id.street,
                'pick_province': sender_id.state_id.name,
                'pick_district': sender_id.district_id.name,
                'pick_ward': sender_id.ward_id.name,
                'pick_tel': standardization_e164(sender_id.mobile or sender_id.phone),
                'tel': standardization_e164(picking.partner_id.mobile or picking.partner_id.phone),
                'name': picking.partner_id.name,
                'address': picking.partner_id.street,
                'province': picking.partner_id.state_id.name,
                'district': picking.partner_id.district_id.name,
                'ward': picking.partner_id.ward_id.name,
                'hamlet': 'Khác',
                'note': picking.remarks or '',
                'is_freeship': 1 if picking.ghtk_payer_type == 'SENDER' else 0,
                'weight_option': 'gram' if self.base_weight_unit == 'G' else 'kilogram',
                'value': math.ceil(picking.sale_id.amount_total),
                'pick_option': 'cod',
                'actual_transfer_method': picking.ghtk_transport_type,
                'transport': picking.ghtk_transport_type,
            },
            'products': [{
                'name': line.product_id.name,
                'weight': math.ceil(self.convert_weight(line.product_id.weight, self.base_weight_unit)),
                'quantity': int(line.quantity),
                'price': math.ceil(line.product_id.list_price),
                'product_code': line.product_id.default_code or line.product_id.name
            } for line in picking.move_ids_without_package]
        }
        if picking.ghtk_special_service_type_ids:
            payload['order']['tags[]'] = [int(rec.code) for rec in picking.ghtk_special_service_type_ids]
        if picking.ghtk_service_type and picking.ghtk_service_type == 'xfast':
            payload['order']['deliver_option'] = 'xteam'
            payload['order']['pick_session'] = list(data.get('data', {}).keys())[0]
        if picking.ghtk_pick_shift:
            payload['pick_work_shift'] = int(picking.ghtk_pick_shift)
        if picking.ghtk_deliver_shift:
            payload['deliver_work_shift'] = int(picking.ghtk_deliver_shift)
        return payload

    @staticmethod
    def _ghtk_check_available_xfast_service(picking):
        sender_id = picking.picking_type_id.warehouse_id.partner_id
        payload = {
            'pick_province': sender_id.state_id.name,
            'pick_district': sender_id.district_id.name,
            'pick_ward': sender_id.ward_id.name,
            'customer_province': picking.partner_id.state_id.name,
            'customer_district': picking.partner_id.district_id.name,
            'customer_ward': picking.partner_id.ward_id.name,
            'customer_first_address': picking.partner_id.shipping_address
        }
        return payload

    def ghtk_send_shipping(self, pickings):
        data = {}
        for picking in pickings:
            if picking.ghtk_service_type == 'xfast':
                client = Client(Connection(self, get_route_api(self, settings.ghtk_check_xfast_service_route_code.value)))
                data = client.check_available_xfast_service(self._ghtk_check_available_xfast_service(picking))
            client = Client(Connection(self, get_route_api(self, settings.ghtk_create_order_route_code.value)))
            result = client.create_order(self._ghtk_payload_create_order(picking, data))
            status_id = self.env.ref('tangerine_delivery_ghtk.ghtk_status_2')
            picking.write({'delivery_status_id': status_id.id if status_id else False})
            self.env['carrier.ref.order'].sudo().create({'picking_id': picking.id})
            return [{
                'exact_price': result.get('order').get('fee'),
                'tracking_number': result.get('order').get('label')
            }]

    def ghtk_cancel_shipment(self, picking):
        client = Client(Connection(self, get_route_api(self, settings.ghtk_cancel_request_route_code.value)))
        client.cancel_order(picking.carrier_tracking_ref)
        picking.write({'carrier_tracking_ref': False, 'carrier_price': 0.0, 'delivery_status_id': False})
        return notification('success', f'Cancel tracking reference {picking.carrier_tracking_ref} successfully')

    def ghtk_print_order(self, carrier_tracking_ref, layout, size):
        client = Client(Connection(self, get_route_api(self, settings.ghtk_print_order_route_code.value)))
        client.print_order(carrier_tracking_ref, {'original': layout, 'page_size': size})
        return notification('success', f'Cancel tracking reference successfully')

    def ghtk_toggle_prod_environment(self):
        self.ensure_one()
        if self.prod_environment:
            self.domain = settings.domain_production.value
        else:
            self.domain = settings.domain_staging.value