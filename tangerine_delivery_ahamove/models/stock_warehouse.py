from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_base.settings import utils
from ..settings.constants import settings
from ..api.connection import Connection
from ..api.client import Client


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    ahamove_service_ids = fields.One2many('ahamove.service', 'warehouse_id', string='Services')

    def ahamove_service_sync(self):
        try:
            for warehouse in self:
                if not warehouse.partner_id.state_id.ahamove_province_code:
                    raise UserError(_('The address of warehouse not set ahamove code. Please mapping ahamove code'))
                provider_id = warehouse.env['delivery.carrier'].search([
                    ('delivery_type', '=', settings.ahamove_code.value)
                ])
                client = Client(Connection(provider_id))
                route_id = utils.get_route_api(provider_id, settings.service_sync_route_code.value)
                result = client.ahamove_service_synchronous(route_id, warehouse.partner_id.state_id.ahamove_province_code)
                payload_service = []
                for service in result:
                    service_id = warehouse.env['ahamove.service'].search([
                        ('code', '=', service.get('_id')),
                        ('warehouse_id', '=', warehouse.id)
                    ])
                    if not service_id:
                        payload_service_request = []
                        for request in service.get('requests'):
                            request_id = warehouse.env['ahamove.service.request'].search([
                                ('code', '=', request.get('_id'))
                            ])
                            if not request_id:
                                payload_service_request.append(
                                    (0, 0, {'name': request.get('name'), 'code': request.get('_id')})
                                )
                            else:
                                warehouse.env['ahamove.service.request'].write({
                                    'name': request.get('name'), 'code': request.get('_id')
                                })
                        payload_service.append({
                            'name': service.get('name'),
                            'code': service.get('_id'),
                            'description': service.get('description_vi_vn'),
                            'active': service.get('enable'),
                            'warehouse_id': warehouse.id,
                            'request_ids': payload_service_request
                        })
                    else:
                        service_id.write({
                            'name': service.get('name'),
                            'code': service.get('_id'),
                            'active': service.get('enable')
                        })
                if payload_service:
                    warehouse.env['ahamove.service'].create(payload_service)
        except Exception as e:
            raise UserError(ustr(e))
