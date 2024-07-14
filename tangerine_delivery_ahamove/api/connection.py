# -*- coding: utf-8 -*-
import requests
import logging
from dataclasses import dataclass
from typing import Any
from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_base.settings.status import status

_logger = logging.getLogger(__name__)


@dataclass
class Connection:
    provider: models

    @staticmethod
    def execute_restful(url: str, method: str, headers: dict[str, Any], **kwargs):
        try:
            _logger.info(f'Execute API: {method}: {url}')
            if method == 'POST':
                response = requests.post(url=url, headers=headers, json=kwargs)
            elif method == 'GET':
                response = requests.get(url=url, headers=headers, params=kwargs)
            elif method == 'DELETE':
                response = requests.delete(url=url, headers=headers, data=kwargs)
            elif method == 'PUT':
                response = requests.put(url=url, headers=headers, data=kwargs)
            else:
                raise UserError(_(f'The Grab Express not support method: {method}'))
            response.raise_for_status()
            if response.status_code not in [status.HTTP_200_OK.value, status.HTTP_204_NO_CONTENT.value]:
                raise UserError(response.text)
            if response.status_code == status.HTTP_204_NO_CONTENT.value:
                return True
            result = response.json()
            return result
        except Exception as e:
            raise UserError(ustr(e))
