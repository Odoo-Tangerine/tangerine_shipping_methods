# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    district_id = fields.Many2one(comodel_name='res.country.district', string='District',
                                  domain="[('state_id','=', state_id)]")
    ward_id = fields.Many2one(comodel_name='res.country.ward', string='Ward',
                              domain="[('district_id', '=', district_id)]")

    shipping_address = fields.Char(compute='_compute_complete_shipping_address')

    @staticmethod
    def replace_address_name(pattern, name):
        for long_text, short_text in pattern.items():
            name = re.sub(long_text, short_text, name, flags=re.IGNORECASE)
        return name

    @staticmethod
    def replace_province_text(name):
        return re.sub(r'\btp\s+', '', name, flags=re.IGNORECASE)

    @api.depends('street', 'ward_id', 'district_id', 'state_id')
    def _compute_complete_shipping_address(self):
        for record in self:
            record.shipping_address = ''
            if record.street:
                record.shipping_address += record.street + ', '
            if record.ward_id:
                pattern = {r'\bphường\s+': 'P.', r'\bxã\s+': 'X.', r'\bthị\s+trấn\s+': 'TT.', r'\bhuyện\s+': 'H.'}
                record.shipping_address += self.replace_address_name(pattern, record.ward_id.name) + ', '
            if record.district_id:
                pattern = {r'\bquận\s+': 'Q.', r'\bhuyện\s+': 'H.', r'\bthị\s+xã\s+': 'TX.', r'\bthành\s+phố\s+': 'TP.'}
                record.shipping_address += self.replace_address_name(pattern, record.district_id.name) + ', '
            if record.state_id:
                record.shipping_address += self.replace_province_text(record.state_id.name) + ', '
            record.shipping_address = record.shipping_address.strip().strip(',')
