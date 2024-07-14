import logging
from odoo.tools import ustr
from odoo.http import request, Controller, route
from odoo.addons.tangerine_delivery_base.settings.utils import authentication, response
from odoo.addons.tangerine_delivery_base.settings.status import status

_logger = logging.getLogger(__name__)


class DeliveriesController(Controller):
    @authentication
    @route('/webhook/v1/delivery/grab', type='json', auth='public', methods=['POST'])
    def grab_callback(self):
        try:
            body = request.dispatcher.jsonrequest
            _logger.info(f'WEBHOOK GRAB START - BODY: {body}')
            picking_id = request.env['stock.picking'].sudo().search([
                ('carrier_tracking_ref', '=', body.get('deliveryID'))
            ])
            if not picking_id:
                _logger.error(f'WEBHOOK GRAB ERROR: The delivery id {body.get("deliveryID")} not found.')
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The delivery id {body.get("deliveryID")} not found.'
                )
            status_id = request.env['delivery.status'].sudo().search([
                ('code', '=', body.get('status')),
                ('provider_id', '=', picking_id.carrier_id.id)
            ])
            if not status_id:
                _logger.error(f'WEBHOOK GRAB ERROR: The status {body.get("status")} invalid.')
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The status {body.get("status")} invalid.'
                )
            payload = {
                'delivery_status_id': status_id.id,
                'grab_tracking_link': body.get('trackURL')
            }
            if body.get('driver'):
                payload.update({
                    'driver_name': body.get('driver').get('name'),
                    'driver_phone': body.get('driver').get('phone'),
                    'grab_driver_license_plate': body.get('driver').get('licensePlate'),
                    'grab_driver_photo_url': body.get('driver').get('photoURL'),
                })
            picking_id.sudo().write(payload)
            _logger.info(f'WEBHOOK GRAB SUCCESS: Receive order callback {body.get("deliveryID")} successfully.')
            return response(
                status=status.HTTP_200_OK.value,
                message=f'Receive order callback {body.get("deliveryID")} successfully.'
            )
        except Exception as e:
            _logger.exception(f'WEBHOOK GRAB EXCEPTION: {ustr(e)}')
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR.value, message=ustr(e))
