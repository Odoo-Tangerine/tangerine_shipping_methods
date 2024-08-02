from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_estimated_weight(self):
        self.ensure_one()
        weight = 0.0
        for order_line in self.order_line.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not l.is_delivery and not l.display_type):
            weight += order_line.product_qty * order_line.product_id.weight
        return weight
