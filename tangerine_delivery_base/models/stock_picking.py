from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    remarks = fields.Char(string='Remarks')
    cash_on_delivery = fields.Boolean(string='COD', default=False)
    cash_on_delivery_amount = fields.Monetary(string='COD Money')
    schedule_order = fields.Boolean(string='Schedule', default=False)
    schedule_pickup_time_from = fields.Datetime(string='Pickup Time From', default=fields.Datetime.now)
    schedule_pickup_time_to = fields.Datetime(string='Pickup Time To')

    driver_name = fields.Char(string='Driver Name', readonly=True)
    driver_phone = fields.Char(string='Driver Phone', readonly=True)
    driver_license_plate = fields.Char(string='Driver License Plate', readonly=True)
    promo_code = fields.Char(string='Promo Code')
    delivery_status_id = fields.Many2one('delivery.status', string='Delivery Status', readonly=True)
    delivery_status_code = fields.Char(related='delivery_status_id.code')

    @api.onchange('cash_on_delivery')
    def _on_change_cash_on_delivery(self):
        for rec in self:
            if rec.cash_on_delivery:
                rec.cash_on_delivery_amount = rec.sale_id.amount_total
            else:
                rec.cash_on_delivery_amount = 0.0
