from odoo import fields, models, api
from ..settings.constants import settings


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    viettelpost_order_payment = fields.Selection(selection=settings.order_payment.value, string='Payment Type')
    viettelpost_product_type = fields.Selection(selection=settings.product_type.value, string='Product Type')
    viettelpost_national_type = fields.Selection(selection=settings.national_type.value, string='Types of Shipments')
    viettelpost_service_request_domain = fields.Binary(default=[], store=False)
    viettelpost_service_id = fields.Many2one('viettelpost.service', string='Service')
    viettelpost_service_extend_id = fields.Many2one('viettelpost.service.extend', string='Service Extend')

    @api.onchange('carrier_id')
    def _onchange_viettelpost_provider(self):
        for rec in self:
            if rec.carrier_id and rec.carrier_id.delivery_type == settings.code.value:
                rec.viettelpost_order_payment = rec.carrier_id.default_viettelpost_order_payment
                rec.viettelpost_product_type = rec.carrier_id.default_viettelpost_product_type
                rec.viettelpost_national_type = rec.carrier_id.default_viettelpost_national_type
                rec.viettelpost_service_id = rec.carrier_id.default_viettelpost_service_id
                rec.viettelpost_service_extend_id = rec.carrier_id.default_viettelpost_service_extend_id

    @api.onchange('viettelpost_service_id')
    def _onchange_viettelpost_service_id(self):
        for rec in self:
            if rec.viettelpost_service_id:
                rec.viettelpost_service_request_domain = [('service_id', '=', rec.viettelpost_service_id.id)]
