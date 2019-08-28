# -*- coding: utf-8 -*-

{
    'name': 'ESCO Enhancments',
    'version': '1.0',
    'author': 'Engineering Solutions/ Balram',
    'category': 'Sales',
    'description': '''
        Customer total invoice paid , due invoice on customer/vendor list view
    ''',
    'website': 'https://www.escoiq.com',
    'depends': ['sale_management','account', 'stock','esco_retail_reports'],
    'data': [
        'security/security.xml',
        'views/res_partner_inherit.xml',
        'views/retail_report_config.xml',
    ],
    'installable': True,
}
