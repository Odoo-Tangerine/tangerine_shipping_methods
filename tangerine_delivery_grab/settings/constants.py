# -*- coding: utf-8 -*-
from enum import Enum
from typing import Final


class settings(Enum):
    domain: Final[str] = 'https://partner-api.grab.com'
    grab_code: Final[str] = 'grab'
    staging_route: Final[str] = 'grab-express-sandbox'
    production_route: Final[str] = 'grab-express'

    tracking_url: Final[str] = 'https://partner-api.grab.com/tracking'
    oauth_route_code: Final[str] = 'oauth_route'
    get_quotes_route_code: Final[str] = 'get_delivery_quotes'
    create_request_route_code: Final[str] = 'create_delivery_request'
    cancel_request_route_code: Final[str] = 'cancel_delivery'

    service_type: Final[list[tuple[str, str]]] = [
        ('INSTANT', 'Instant'),
        ('SAME_DAY', 'Same Day'),
        ('BULK', 'Bulk')
    ]
    default_service_type: Final[str] = 'INSTANT'

    vehicle_type: Final[list[tuple[str, str]]] = [
        ('BIKE', 'Bike'),
        ('CAR', 'Car'),
        ('JUSTEXPRESS', 'Just Express'),
        ('VAN', 'VAN'),
        ('TRUCK', 'Truck'),
        ('TRIKE', 'Trike'),
        ('EBIKE', 'EBike'),
        ('SUV', 'SUV'),
        ('BOXPICKUPTRUCK', 'Box Pickup Truck'),
        ('TRICYCLE', 'Tricycle'),
        ('CYCLE', 'Cycle'),
        ('FOOT', 'Foot'),
    ]
    default_vehicle_type: Final[str] = 'BIKE'

    payment_method: Final[list[tuple[str, str]]] = [
        ('CASHLESS', 'Cashless'),
        ('CASH', 'Cash')
    ]
    default_payment_method: Final[str] = 'CASHLESS'

    payer: Final[list[tuple[str, str]]] = [
        ('SENDER', 'Sender'),
        ('RECIPIENT', 'Recipient')
    ]
    default_payer: Final[str] = 'SENDER'

    cod_type: Final[list[tuple[str, str]]] = [
        ('REGULAR', 'Regular'),
        ('ADVANCED', 'Advanced')
    ]

    default_cod_type: Final[str] = 'REGULAR'

    list_status_cancellation_allowed: Final[str] = ['IN_DELIVERY', 'FAILED', 'CANCELED', 'COMPLETED']
    status_completed: Final[str] = 'COMPLETED'
