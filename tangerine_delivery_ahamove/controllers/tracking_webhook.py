from odoo.tools import ustr
from odoo.http import request, Controller, route
from odoo.addons.tangerine_delivery_base.settings.utils import authentication, response
from odoo.addons.tangerine_delivery_base.settings.status import status


class DeliveriesController(Controller):
    @authentication
    @route('/api/v1/webhook/ahamove', type='json', auth='public', methods=['POST'])
    def ahamove_callback(self):
        try:
            body = request.dispatcher.jsonrequest
            picking_id = request.env['stock.picking'].sudo().search([
                ('carrier_tracking_ref', '=', body.get('_id'))
            ])
            if not picking_id:
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The delivery id {body.get("_id")} not found.'
                )
            status_id = request.env['delivery.status'].sudo().search([
                ('code', '=', body.get('status')),
                ('provider_id', '=', picking_id.carrier_id.id)
            ])
            if not status_id:
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The status {body.get("status")} does not match partner system.'
                )
            payload = {'status_id': status_id.id}
            if body.get('driver'):
                payload.update({
                    'driver_name': body.get('supplier_name'),
                    'driver_phone': body.get('supplier_id')
                })
            picking_id.sudo().write(payload)
        except Exception as e:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR.value, message=ustr(e))
