# -*- coding: utf-8 -*-
from enum import Enum
from typing import Final


class settings(Enum):
    domain_staging = 'https://services-staging.ghtklab.com'
    domain_production = 'https://services.giaohangtietkiem.vn'
    ghtk_code = 'ghtk'

    ghtk_estimate_order_route_code = 'ghtk_estimate_order'
    ghtk_create_order_route_code = 'ghtk_create_order'
    ghtk_check_xfast_service_route_code = 'ghtk_check_available_xfast_service'
    ghtk_cancel_request_route_code = 'ghtk_cancel_request'
    ghtk_print_order_route_code = 'ghtk_print_order'

    payer_type = [
        ('SENDER', 'Sender'),
        ('RECIPIENT', 'Recipient')
    ]

    default_payer_type = 'SENDER'

    transport_type = [
        ('road', 'Road'),
        ('fly', 'Fly')
    ]

    default_transport_type = 'road'

    service_type = [
        ('standard', 'Standard'),
        ('xfast', 'Fast')
    ]

    default_service_type = 'xfast'

    pick_shift = [
        ('1', 'Morning'),
        ('2', 'Noon'),
        ('3', 'Evening')
    ]

    deliver_shift = [
        ('1', 'Morning'),
        ('2', 'Noon'),
        ('3', 'Evening')
    ]

    print_layouts = [
        ('portrait ', 'Portrait'),
        ('landscape', 'Landscape')
    ]

    paper_size = [
        ('A5', 'A5'),
        ('A6', 'A6')
    ]
