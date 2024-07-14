from odoo import fields, models


class CarrierRefOrder(models.Model):
    _inherit = 'carrier.ref.order'

    grab_driver_license_plate = fields.Char(related='picking_id.grab_driver_license_plate', string='License Plate')
    grab_driver_photo_url = fields.Char(related='picking_id.grab_driver_photo_url', string='Photo Url')
