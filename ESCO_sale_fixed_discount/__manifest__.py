# -*- coding: utf-8 -*-

{
    'name': 'ESCO Sale Fixed Discount',
    'version': '1.0',
    'author': 'Engineering Solutions',
    'category': 'Sales',
    'description': '''
        Sale order line Fixed amount Discount
    ''',
    'website': 'https://www.escoiq.com',
    'depends': ['sale','account','ESCO_ReTail_Reports'],
    'data': [
        'security/security.xml',
        'views/sale_order_line_inherit.xml',
        'views/retial_report_config.xml',
    ],
    'installable': True,
}
