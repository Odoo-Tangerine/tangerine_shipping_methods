from odoo import fields, models
from ..settings.constants import settings


class PrintOrderWizard(models.TransientModel):
    _name = 'viettelpost.print.order.wizard'
    _description = 'Viettelpost Print Order Wizard'

    picking_id = fields.Many2one('stock.picking', required=True, string='Picking')
    delivery_type = fields.Selection(related='picking_id.delivery_type')
    carrier_tracking_ref = fields.Char(related='picking_id.carrier_tracking_ref', string='Carrier Tracking Ref')
    paper_type = fields.Selection(
        selection=settings.paper_print.value,
        string='Paper Type',
        default='a5',
        required=True
    )

    def print_order_viettelpost(self):
        url = self.picking_id.carrier_id.viettelpost_print_order(self.carrier_tracking_ref, self.paper_type)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'close': True
        }