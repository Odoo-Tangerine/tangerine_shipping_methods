from odoo import models, fields


class District(models.Model):
    _name = 'res.country.district'
    _description = 'District'
    _order = 'code'

    name = fields.Char('District name')
    code = fields.Char(string='Code', required=True)
    slug = fields.Char(string='Slug')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country', required=True)
    type = fields.Selection(selection=[
        ('0', 'Quận'),
        ('1', 'Huyện'),
        ('2', 'Thị xã'),
        ('3', 'Thành Phố')
    ], string='Type')
    ward_ids = fields.One2many('res.country.ward', 'district_id')
