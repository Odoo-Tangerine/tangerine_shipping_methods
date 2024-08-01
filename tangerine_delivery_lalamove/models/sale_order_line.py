from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lalamove_quotation_data = fields.Char(string='Lalamove Quotation Data')
