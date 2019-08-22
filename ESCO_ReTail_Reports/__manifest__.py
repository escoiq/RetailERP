# -*- coding: utf-8 -*-

{
    'name': 'ESCO Report',
    'version': '1.0',
    'author': 'Sachin Kotak',
    'category': '',
    'description': '''
        Custom Rrport module
    ''',
    'depends': ['account','sale','base_setup'],
    'data': [
        'data/service_cron_reverse.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/stock_custom_report.xml',
        'views/retial_report_config.xml',
    ],
    'installable': True,
}
