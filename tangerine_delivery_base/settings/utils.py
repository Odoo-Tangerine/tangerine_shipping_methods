# -*- coding: utf-8 -*-
import re
import pytz
import functools
from typing import NamedTuple, Any, Optional
from urllib.parse import urlencode, unquote_plus
from odoo import _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.http import request
from .status import status


def response(status, message, data=None):
    response = {'status': status, 'message': message}
    if data:
        response.update({'data': data})
    return response


def authentication(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get('Authorization')
        access_token = re.sub(r'^Bearer\s+', '', access_token)
        if not access_token:
            return response(
                message='The header Authorization missing',
                status=status.HTTP_401_UNAUTHORIZED.value
            )
        carrier_id = request.env['delivery.carrier'].sudo().search([('webhook_access_token', '=', access_token)])
        if not carrier_id:
            return response(
                message=f'The access token seems to have invalid.',
                status=status.HTTP_403_FORBIDDEN.value
            )
        request.update_env(SUPERUSER_ID)
        return func(self, *args, **kwargs)
    return wrap


def notification(notification_type: str, message: str):
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'type': notification_type,
            'message': _(message),
            'next': {'type': 'ir.actions.act_window_close'},
        }
    }


def get_route_api(provider_id, code):
    route_id = provider_id.route_api_ids.search([('code', '=', code)])
    if not route_id:
        raise UserError(_(f'Route {code} not found'))
    return route_id


def datetime_to_rfc3339(dt, time_zone):
    dt = dt.astimezone(pytz.timezone(time_zone))
    return dt.isoformat()


def standardization_e164(phone_number):
    phone_number = re.sub(r'[^\d+]', '', phone_number)
    if phone_number.startswith('0'):
        phone_number = f'84{phone_number[1:]}'
    elif phone_number.startswith('+'):
        phone_number = phone_number[1:]
    return phone_number


class URLBuilder(NamedTuple):
    host: str
    routes: str
    query_params: str
    path_params: str

    @classmethod
    def _add_path_params(cls, param_name, v=None):
        if not v: return v
        elif not isinstance(v, str): raise TypeError(f'{param_name} must be a str')
        return v

    @classmethod
    def _add_query_params(cls, param_name, v=None):
        if not v: return v
        elif not isinstance(v, dict): raise TypeError(f'{param_name} must be a dict')
        return urlencode(v)

    @classmethod
    def _add_routes(cls, param_name, v=None):
        if not v: return ''
        elif not isinstance(v, list): raise TypeError(f'{param_name} must be a list')
        return ''.join(v)

    @classmethod
    def _define_host(cls, param_name, v):
        if not v: raise KeyError(f'Key {param_name} missing')
        elif not isinstance(v, str): raise TypeError(f'Key {param_name} must be a string')
        return v

    @classmethod
    def to_url(cls, instance, is_unquote=None):
        url = f'{instance.host}{instance.routes}'
        if instance.query_params:
            if is_unquote:
                params = re.sub(r"'", '"', unquote_plus(instance.query_params))
            else:
                params = re.sub(r"'", '"', instance.query_params)
            return f'{url}?{params}'
        if instance.path_params:
            return f'{url}/{instance.path_params}'
        return url

    @classmethod
    def builder(cls, host, routes, query_params=None, path_params=None, is_unquote=None):
        instance = cls(
            cls._define_host('host', host),
            cls._add_routes('routes', routes),
            cls._add_query_params('query_params', query_params),
            cls._add_path_params('path_params', path_params)
        )
        return cls.to_url(instance, is_unquote)
