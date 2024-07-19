from odoo import models
from ..settings.constants import settings


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_action_view_picking(self, pickings):
        action = super(SaleOrder, self)._get_action_view_picking(pickings)
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        if picking_id.carrier_id.delivery_type == settings.grab_code.value:
            action['context'].update({
                'default_grab_service_type': picking_id.carrier_id.default_grab_service_type,
                'default_grab_vehicle_type': picking_id.carrier_id.default_grab_vehicle_type,
                'default_grab_payment_method': picking_id.carrier_id.default_grab_payment_method,
                'default_grab_payer': picking_id.carrier_id.default_grab_payer,
            })
        return action
