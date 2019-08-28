# -*- coding: utf-8 -*-

{
    'name': 'ESCO Account',
    'version': '1.0',
    'author': 'Sachin Kotak',
    'category': '',
    'description': '''

    ''',
    'website': 'mitesh4829@gmail.com',
    'depends': ['account','stock','esco_retail_reports'],
    'data': [
        'report/report_invoice.xml',
        'security/security_view.xml',
        'view/retial_report_config_inherit.xml',
        'view/account_register.xml',
        'view/account_invoice_inherit.xml',
    ],
    'installable': True,
}