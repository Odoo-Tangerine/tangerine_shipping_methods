# -*- coding: utf-8 -*-
{
    'name': 'Subdivisions of Vietnam',
    'summary': """The Subdivisions of Vietnam module is an extension for the Odoo system designed to provide a comprehensive database of addresses in Vietnam.""",
    'author': 'Long Duong Nhat',
    'category': 'Extra Tools',
    'support': 'odoo.tangerine@gmail.com',
    'version': '17.0.1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/res_country_state_data.xml',
        'data/res.country.district.csv',
        'data/res.country.ward.csv',
        'views/res_country_district_views.xml',
        'views/res_country_ward_views.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'views/menus.xml'
    ],
    'images': ['static/description/thumbnail.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}