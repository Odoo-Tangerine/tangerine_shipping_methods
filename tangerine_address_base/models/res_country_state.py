import re
from odoo import models, fields


class CountryState(models.Model):
    _inherit = 'res.country.state'
    _order = 'code_ext'

    def _make_code_ext(self):
        for record in self:
            if not record.code_ext:
                record.code_ext = record.code

    code_ext = fields.Char(string='State Code', required=True, compute=_make_code_ext, store=True)
