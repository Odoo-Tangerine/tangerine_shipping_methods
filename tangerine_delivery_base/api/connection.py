# -*- coding: utf-8 -*-
import requests
import logging
from dataclasses import dataclass
from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_base.settings.status import status

_logger = logging.getLogger(__name__)


@dataclass
class Connection:
    provider: models
    endpoint: models

    def execute_restful(self, url, method, headers, **kwargs):
        try:
            _logger.warning(f'[{self.provider.delivery_type.upper()}] - [EXECUTE API]: {method}: {url} - Header: {headers} - Body: {kwargs}')
            if method == 'POST':
                response = requests.post(url=url, headers=headers, json=kwargs)
            elif method == 'GET':
                response = requests.get(url=url, headers=headers, params=kwargs)
            elif method == 'DELETE':
                response = requests.delete(url=url, headers=headers, json=kwargs)
            elif method == 'PUT':
                response = requests.put(url=url, headers=headers, data=kwargs)
            elif method == 'PATCH':
                response = requests.patch(url=url, headers=headers, json=kwargs)
            else:
                raise UserError(_(f'The interface not support method: {method}'))
            response.raise_for_status()
            if response.status_code not in range(status.HTTP_200_OK.value, status.HTTP_300_MULTIPLE_CHOICES.value):
                raise UserError(response.text)
            if response.status_code == status.HTTP_204_NO_CONTENT.value:
                return True
            result = response.json()
            _logger.info(f'RESULT EXECUTE API: {result}')
            return result
        except Exception as e:
            raise UserError(ustr(e))
