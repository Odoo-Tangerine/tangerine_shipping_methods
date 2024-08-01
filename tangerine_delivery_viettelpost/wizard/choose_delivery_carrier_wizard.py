from odoo import fields, models, api, _
from odoo.exceptions import UserError
from ..settings.constants import settings


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    viettelpost_service_id = fields.Many2one('viettelpost.service', string='Service')
    viettelpost_service_extend_id = fields.Many2one('viettelpost.service.extend', string='Service Extend')
    viettelpost_national_type = fields.Selection(selection=settings.national_type.value, string='National Type')
    viettelpost_product_type = fields.Selection(selection=settings.product_type.value, string='Product Type')

    @api.onchange('carrier_id', 'total_weight')
    def _onchange_viettelpost_provider(self):
        res = super(ChooseDeliveryCarrier, self)._onchange_carrier_id()
        for rec in self:
            if rec.carrier_id and rec.carrier_id.delivery_type == settings.code.value:
                rec.viettelpost_product_type = rec.carrier_id.default_viettelpost_product_type
                rec.viettelpost_national_type = rec.carrier_id.default_viettelpost_national_type
                rec.viettelpost_service_id = rec.carrier_id.default_viettelpost_service_id
                rec.viettelpost_service_extend_id = rec.carrier_id.default_viettelpost_service_extend_id
        return res

    @api.onchange('viettelpost_service_id')
    def _onchange_viettelpost_service_id(self):
        for rec in self:
            if rec.viettelpost_service_id:
                return {
                    'domain': {
                        'viettelpost_service_extend_id': [('service_id', '=', rec.viettelpost_service_id.id)]
                    },
                }

    def _get_shipment_rate(self):
        if self.carrier_id.delivery_type == settings.code.value:
            context = dict(self.env.context)
            context.update({
                'viettelpost_service_code': self.viettelpost_service_id.code or self.carrier_id.default_viettelpost_service_id.code or settings.default_service_type.value,
                'viettelpost_service_extend_code': self.viettelpost_service_extend_id.code or None,
                'viettelpost_national_type': self.viettelpost_national_type or self.carrier_id.default_viettelpost_national_type or settings.default_national_type.value,
                'viettelpost_product_type': self.viettelpost_product_type or self.carrier_id.default_viettelpost_product_type or settings.default_product_type.value,
            })
            self.env.context = context
        return super(ChooseDeliveryCarrier, self)._get_shipment_rate()
