# -*- coding: utf-8 -*-
{
    'name': 'Lalamove Integration',
    'summary': """Lalamove Integration will allow Odooers to easily place, cancel, get quotes, and track the order via simple integration.""",
    'author': 'Long Duong Nhat',
    'category': 'Inventory/Delivery',
    'support': 'odoo.tangerine@gmail.com',
    'version': '17.0.1.0',
    'depends': ['tangerine_delivery_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/lalamove_regional_data.xml',
        'data/delivery_lalamove_data.xml',
        'data/lalamove_route_api_data.xml',
        'data/lalamove_status_data.xml',
        'data/res_partner_data.xml',
        'data/ir_cron.xml',
        'wizard/choose_delivery_carrier_wizard_views.xml',
        'views/delivery_lalamove_views.xml',
        'views/stock_picking_views.xml',
    ],
    'images': ['static/description/thumbnail.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'currency': 'USD',
    'price': 119.00
}