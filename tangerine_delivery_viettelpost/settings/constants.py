# -*- coding: utf-8 -*-
from enum import Enum
from typing import Final


class settings(Enum):
    domain_production: Final[str] = 'https://partner.viettelpost.vn'
    domain_staging: Final[str] = 'https://partnerdev.viettelpost.vn'
    tracking_url: Final[str] = 'https://viettelpost.com.vn/tra-cuu-hanh-trinh-don'
    code: Final[str] = 'viettelpost'

    get_short_term_token_route: Final[str] = 'viettelpost_get_short_term_token'
    get_long_term_token_route: Final[str] = 'viettelpost_get_long_term_token'
    service_sync_route: Final[str] = 'viettelpost_service_sync'
    service_extend_sync_route: Final[str] = 'viettelpost_service_extend_sync'
    get_matching_service_route: Final[str] = 'viettelpost_get_matching_service'
    estimate_cost_route: Final[str] = 'viettelpost_estimate_cost'
    create_order_route: Final[str] = 'viettelpost_create_order'
    update_order_route: Final[str] = 'viettelpost_update_order'
    viettelpost_print_order_route: Final[str] = 'viettelpost_print_order'

    url_print_a5: Final[str] = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=1&bill={}&showPostage=1'
    url_print_a6: Final[str] = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=2&bill={}&showPostage=1'
    url_print_a7: Final[str] = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=1001&bill={}&showPostage=1'

    product_type: Final[list[tuple[str, str]]] = [
        ('TH', 'Letter'),
        ('HH', 'Goods')
    ]
    default_product_type: Final[str] = 'HH'

    national_type: Final[list[tuple[str, str]]] = [
        ('0', 'International'),
        ('1', 'Domestic')
    ]
    default_national_type: Final[str] = '1'

    order_payment: Final[list[tuple[str, str]]] = [
        ('1', 'No collection'),
        ('2', 'Collect money for goods and delivery'),
        ('3', 'Collect money for goods'),
        ('4', 'Collect money for delivery')
    ]
    default_order_payment: Final[str] = '1'
    default_service_type: Final[str] = 'VCN'

    list_status_cancellation_allowed: Final[str] = ['IN_DELIVERY', 'FAILED', 'CANCELED', 'COMPLETED']
    status_completed: Final[str] = 'COMPLETED'
