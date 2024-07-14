from odoo import models, fields, api


class AhamoveService(models.Model):
    _name = 'ahamove.service'
    _description = 'Ahamove Service'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)
    active = fields.Boolean(defaut=True)
    description = fields.Char(string='Description')
    request_ids = fields.One2many('ahamove.service.request', 'service_id', 'Requests')

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'[{rec.code}] - {rec.name}'

    _sql_constraints = [
        ('code_and_warehouse_uniq', 'unique (code, warehouse_id)', 'The service already exists!'),
    ]


class AhamoveServiceRequest(models.Model):
    _name = 'ahamove.service.request'
    _description = 'Ahamove Service Request'

    service_id = fields.Many2one('ahamove.service', string='Service')
    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)
    description = fields.Char(string='Description')

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'[{rec.code}] - {rec.name}'

    _sql_constraints = [
        ('code_and_service_uniq', 'unique (code, service_id)', 'The request already exists!'),
    ]
