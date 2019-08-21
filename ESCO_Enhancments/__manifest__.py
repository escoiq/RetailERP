# -*- coding: utf-8 -*-

{
    'name': 'ESCO Enhancments',
    'version': '1.0',
    'author': 'Engineering Solutions',
    'category': 'Sales',
    'description': '''
        Customer total invoice paid , due invoice on customer/vendor list view
    ''',
    'website': 'https://www.escoiq.com',
    'depends': ['sale','account','stock','ESCO_ReTail_Reports'],
    'data': [
        'security/security.xml',
        'views/res_partner_inherit.xml',
        'views/retial_report_config.xml',
    ],
    'installable': True,
}
