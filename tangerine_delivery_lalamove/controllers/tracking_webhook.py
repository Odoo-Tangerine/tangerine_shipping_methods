import logging
from odoo.tools import ustr
from odoo.http import request, Controller, route
from odoo.addons.tangerine_delivery_base.settings.utils import authentication, response
from odoo.addons.tangerine_delivery_base.settings.status import status
from ..settings.constants import settings

_logger = logging.getLogger(__name__)


class DeliveriesController(Controller):
    @authentication(settings.lalamove_code.value)
    @route(['/webhook/v1/delivery/lalamove', '/webhook/v1/delivery/lalamove/<string:access_token>'], type='json', auth='public', methods=['POST'])
    def lalamove_callback(self):
        try:
            body = request.jsonrequest
            _logger.info(f'WEBHOOK LALAMOVE START - BODY: {body}')
            if body.get('data') and body.get('data').get('order') and body.get('data').get('order').get('orderId'):
                order_id = body.get('data').get('order').get('orderId')
            else:
                return response(
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY.value,
                    message=f'The delivery id is required.'
                )
            picking_id = request.env['stock.picking'].sudo().search([('carrier_tracking_ref', '=', order_id)])
            if not picking_id:
                _logger.error(f'WEBHOOK LALAMOVE ERROR: The delivery id {order_id} not found.')
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The delivery id {order_id} not found.'
                )
            payload = {}
            if body.get('eventType') == settings.webhook_order_status_changed.value:
                if body.get('data') and body.get('data').get('order') and body.get('data').get('order').get('status'):
                    deliver_status = body.get('data').get('order').get('status')
                else:
                    return response(
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY.value,
                        message=f'The status is required.'
                    )
                status_id = request.env['delivery.status'].sudo().search([
                    ('code', '=', deliver_status),
                    ('provider_id', '=', picking_id.carrier_id.id)
                ])
                if not status_id:
                    _logger.error(f'WEBHOOK LALAMOVE ERROR: The status {status} invalid.')
                    return response(
                        status=status.HTTP_400_BAD_REQUEST.value,
                        message=f'The status {deliver_status} invalid.'
                    )
                payload = {'delivery_status_id': status_id.id}
                if not picking_id.lalamove_tracking_link and body.get('data').get('order').get('shareLink'):
                    payload.update({'lalamove_tracking_link': body.get('data').get('order').get('shareLink')})
            if body.get('eventType') == settings.webhook_driver_assigned.value:
                if body.get('data').get('driver'):
                    payload.update({
                        'driver_name': body.get('data').get('driver').get('name'),
                        'driver_phone': body.get('data').get('driver').get('phone'),
                        'driver_license_plate': body.get('data').get('driver').get('plateNumber')
                    })
            if payload:
                picking_id.sudo().write(payload)
            _logger.info(f'WEBHOOK LALAMOVE SUCCESS: Receive order callback {order_id} successfully.')
            return response(
                status=status.HTTP_200_OK.value,
                message=f'Receive order callback {order_id} successfully.'
            )
        except Exception as e:
            _logger.exception(f'WEBHOOK LALAMOVE EXCEPTION: {ustr(e)}')
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR.value, message=ustr(e))
