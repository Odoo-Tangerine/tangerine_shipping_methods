# -*- coding: utf-8 -*-
import time
import math
import threading
from datetime import datetime, timedelta
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_base.settings.utils import (
    datetime_to_rfc3339,
    standardization_e164,
    get_route_api,
    notification
)
from odoo.addons.tangerine_delivery_base.api.connection import Connection
from ..settings.constants import settings
from ..api.client import Client


class ProviderGrab(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('grab', 'Grab Express')
    ], ondelete={'grab': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    grab_partner_id = fields.Char(string='PartnerID')
    grab_client_id = fields.Char(string='ClientID')
    grab_client_secret = fields.Char(string='Client Secret')
    grab_grant_type = fields.Char(string='Grant Type')
    grab_scope = fields.Char(string='Scope')
    grab_token_type = fields.Char(string='Token Type')
    grab_expire_token_date = fields.Datetime(string='Expire Token Date', readonly=True)

    default_grab_payer = fields.Selection(selection=settings.payer.value, string='Payer')
    default_grab_service_type = fields.Selection(selection=settings.service_type.value, string='Service Type')
    default_grab_vehicle_type = fields.Selection(selection=settings.vehicle_type.value, string='Vehicle Type')
    default_grab_payment_method = fields.Selection(selection=settings.payment_method.value, string='Payment Method')

    @staticmethod
    def _compute_expires_seconds_to_datetime(expires_times):
        return datetime.now() + timedelta(seconds=expires_times)

    def _update_cron_refresh_token(self, expires_times):
        time.sleep(10)
        with self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            cron = self.env.ref('tangerine_delivery_grab.ir_cron_refresh_access_token_grab', raise_if_not_found=False)
            if cron:
                cron.sudo().write({
                    'nextcall': datetime.now() + timedelta(seconds=expires_times),
                    'active': True
                })

    def grab_get_access_token(self):
        try:
            self.ensure_one()
            if not self.grab_client_id:
                raise UserError(_('The field ClientID is required'))
            elif not self.grab_client_secret:
                raise UserError(_('The field Client Secret is required'))
            elif not self.grab_grant_type:
                raise UserError(_('The field Grant Type is required'))
            elif not self.grab_scope:
                raise UserError(_('The field Scope is required'))
            client = Client(Connection(self, get_route_api(self, settings.oauth_route_code.value)))
            result = client.get_access_token({
                'client_id': self.grab_client_id,
                'client_secret': self.grab_client_secret,
                'grant_type': self.grab_grant_type,
                'scope': self.grab_scope
            })
            self.write({
                'grab_token_type': result.get('token_type'),
                'access_token': result.get('access_token'),
                'grab_expire_token_date': self._compute_expires_seconds_to_datetime(result.get('expires_in'))
            })
            threaded_update_cron = threading.Thread(target=lambda: self._update_cron_refresh_token(int(result.get('expires_in'))))
            threaded_update_cron.start()
            return notification('success', 'Get access token successfully')
        except Exception as e:
            raise UserError(ustr(e))

    @staticmethod
    def _grab_building_address(address, city_code):
        street, ward, district, province = address.split(',')
        return {
            'address': address,
            'cityCode': city_code,
            'address_L3': ward,
            'address_L2': district,
            'address_L1': province,
            'coordinates': {}
        }

    def _grab_payload_delivery_quotes(self, order):
        payload = {
            'origin': self._grab_building_address(
                address=order.warehouse_id.partner_id.shipping_address,
                city_code=order.warehouse_id.partner_id.state_id.grab_city_code
            ),
            'destination': self._grab_building_address(
                address=order.partner_shipping_id.shipping_address,
                city_code=order.partner_shipping_id.state_id.grab_city_code
            ),
            'packages': [{
                'name': line.product_id.name,
                'description': line.name,
                'quantity': int(line.product_uom_qty),
                'price': int(line.price_subtotal),
                'dimensions': {
                    'height': 0,
                    'width': 0,
                    'depth': 0,
                    'weight': math.ceil(self.convert_weight(line.product_id.weight, self.base_weight_unit))
                }
            } for line in order.order_line if not line.is_delivery]
        }
        if order.env.context.get('grab_service_type'):
            payload.update({'serviceType': order.env.context.get('grab_service_type')})
        if order.env.context.get('grab_vehicle_type'):
            payload.update({'vehicleType': order.env.context.get('grab_vehicle_type')})
        return payload

    def grab_rate_shipment(self, order):
        client = Client(Connection(self, get_route_api(self, settings.get_quotes_route_code.value)))
        result = client.get_delivery_quotes(payload=self._grab_payload_delivery_quotes(order))
        return {
            'success': True,
            'price': result.get('quotes')[0].get('amount'),
            'error_message': False,
            'warning_message': False
        }

    @staticmethod
    def _validate_picking(picking):
        if not picking.partner_id.phone and not picking.partner_id.mobile:
            raise UserError(_('The number phone of recipient is required.'))
        if picking.promo_code and not picking.grab_payment_method:
            raise UserError(_('You are using a promo code, please select a payment method. This is required.'))
        elif picking.grab_payer == 'RECIPIENT' and picking.grab_payment_method == 'CASHLESS':
            raise UserError(_('Sending a RECIPIENT value for CASHLESS payments will result in an error.'))
        elif picking.cash_on_delivery and picking.cash_on_delivery_amount <= 0.0:
            raise UserError(_('The cash on delivery amount must be greater than 0.'))
        elif picking.schedule_order and not picking.schedule_pickup_time_from:
            raise UserError(_('You are using Scheduled for Order. Please select the pickup time from.'))
        elif picking.schedule_order and not picking.schedule_pickup_time_to:
            raise UserError(_('You are using Scheduled for Order. Please select the pickup time to.'))
        elif picking.schedule_order and (picking.schedule_pickup_time_from >= picking.schedule_pickup_time_to):
            raise UserError(_('The delivery time in the future must be greater than the present time.'))

    def _grab_payload_create_delivery_request(self, picking):
        self._validate_picking(picking)
        payload = {
            'merchantOrderID': picking.origin,
            'serviceType': picking.grab_service_type,
            'vehicleType': picking.grab_vehicle_type,
            'codType': picking.grab_cod_type or '',
            'paymentMethod': picking.grab_payment_method,
            'payer': picking.grab_payer,
            'highValue': picking.grab_high_value,
            'packages': [{
                'name': line.name,
                'description': line.name,
                'quantity': int(line.quantity),
                'dimensions': {
                    'height': 0,
                    'width': 0,
                    'depth': 0,
                    'weight': math.ceil(self.convert_weight(line.product_id.weight, self.base_weight_unit))
                }
            } for line in picking.move_ids_without_package],
            'sender': {
                'firstName': picking.picking_type_id.warehouse_id.partner_id.name,
                'phone': standardization_e164(
                    picking.picking_type_id.warehouse_id.partner_id.phone or picking.picking_type_id.warehouse_id.partner_id.mobile
                )
            },
            'recipient': {
                'firstName': picking.partner_id.name,
                'phone': standardization_e164(picking.partner_id.phone or picking.partner_id.mobile)
            },
            'origin': self._grab_building_address(
                address=picking.picking_type_id.warehouse_id.partner_id.shipping_address,
                city_code=picking.picking_type_id.warehouse_id.partner_id.state_id.grab_city_code
            ),
            'destination': self._grab_building_address(
                address=picking.picking_type_id.warehouse_id.partner_id.shipping_address,
                city_code=picking.picking_type_id.warehouse_id.partner_id.state_id.grab_city_code
            ),
        }
        if picking.cash_on_delivery:
            payload.update({'cashOnDelivery': {'amount': picking.cash_on_delivery_amount}})
        if picking.schedule_order:
            payload.update({
                'schedule': {
                    'pickupTimeFrom': datetime_to_rfc3339(picking.schedule_pickup_time_from, picking.env.user.tz),
                    'pickupTimeTo': datetime_to_rfc3339(picking.schedule_pickup_time_to, picking.env.user.tz)
                }
            })
        return payload

    def grab_send_shipping(self, pickings):
        client = Client(Connection(self, get_route_api(self, settings.create_request_route_code.value)))
        for picking in pickings:
            result = client.create_delivery_request(self._grab_payload_create_delivery_request(picking))
            status_id = self.env.ref('tangerine_delivery_grab.grab_status_queueing') if picking.schedule_order else self.env.ref('tangerine_delivery_grab.grab_status_allocating')
            picking.write({'delivery_status_id': status_id.id if status_id else False})
            self.env['carrier.ref.order'].sudo().create({'picking_id': picking.id})
            return [{
                'exact_price': result.get('quote').get('amount'),
                'tracking_number': result.get('deliveryID')
            }]

    @staticmethod
    def grab_get_tracking_link(picking):
        return picking.grab_tracking_link

    def grab_cancel_shipment(self, picking):
        if picking.delivery_status_id.code in settings.list_status_cancellation_allowed.value:
            raise UserError(_(f'You cannot cancel while the order is in {picking.delivery_status_id.name} status'))
        client = Client(Connection(self, get_route_api(self, settings.cancel_request_route_code.value)))
        client.cancel_delivery(picking.carrier_tracking_ref)
        picking.write({'carrier_tracking_ref': False, 'carrier_price': 0.0})
        return notification('success', f'Cancel tracking reference {picking.carrier_tracking_ref} successfully')

    def grab_toggle_prod_environment(self):
        self.ensure_one()
        data = []
        for route_id in self.route_api_ids:
            item = route_id.route.split('/')
            if item[1] == 'grabid': continue
            item[1] = settings.production_route.value if self.prod_environment else settings.staging_route.value
            data.append((1, route_id.id, {'route': '/'.join(item)}))
        if data:
            self.write({'route_api_ids': data})

    def _grab_get_default_custom_package_code(self):...

