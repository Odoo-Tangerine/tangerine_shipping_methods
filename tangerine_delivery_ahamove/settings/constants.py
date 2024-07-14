# -*- coding: utf-8 -*-
from enum import Enum
from typing import Final


class settings(Enum):
    domain_staging: Final[str] = 'https://apistg.ahamove.com'
    domain_production: Final[str] = 'https://api.ahamove.com'
    tracking_url_staging: Final[str] = 'https://cloudstg.ahamove.com'
    tracking_url_production: Final[str] = 'https://cloud.ahamove.com'
    ahamove_code: Final[str] = 'ahamove'

    get_token_route_code: Final[str] = 'get_token'
    estimate_order_route_code: Final[str] = 'estimate_order'
    create_order_route_code: Final[str] = 'create_order'
    cancel_order_route_code: Final[str] = 'cancel_order'
    city_sync_route_code: Final[str] = 'city_sync'
    service_sync_route_code: Final[str] = 'service_sync'

    payment_method: Final[list[tuple[str, str]]] = [
        ('BALANCE', 'BALANCE'),
        ('CASH', 'CASH'),
        ('CASH_BY_RECIPIENT', 'CASH BY RECIPIENT')
    ]
    default_payment_method: Final[str] = 'BALANCE'

    list_status_cancellation_allowed: Final[str] = ['ASSIGNING', 'ACCEPTED', 'CONFIRMING', 'PAYING', 'IDLE']
    status_completed: Final[str] = 'COMPLETED'
    cancel_reason: Final[str] = 'Merchant asks for order cancellation'
    cancel_reason_code: Final[str] = 'partner_merchant_asks_for_order_cancellation'
