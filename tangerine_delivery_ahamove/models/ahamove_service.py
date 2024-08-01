from odoo import models, fields, api


class AhamoveService(models.Model):
    _name = 'ahamove.service'
    _description = 'Ahamove Service'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)
    active = fields.Boolean(default=True)
    description = fields.Char(string='Description')
    request_ids = fields.One2many('ahamove.service.request', 'service_id', 'Requests')

    def name_get(self):
        return [(rec.id, f'[{rec.code}] - {rec.name}') for rec in self]

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
    type_of_request = fields.Char(string='Type of Request')

    def name_get(self):
        return [(rec.id, f'[{rec.code}] - {rec.name}') for rec in self]

    _sql_constraints = [
        ('code_and_service_uniq', 'unique (code, service_id)', 'The request already exists!'),
    ]
