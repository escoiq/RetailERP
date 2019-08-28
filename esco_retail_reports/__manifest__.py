    # -*- coding: utf-8 -*-

{
    'name': 'Report',
    'version': '1.0',
    'author': 'Balram',
    'category': '',
    'description': '''
        Custom Report module
        Activate It from Settings > ESCO settings
        Visible in Invoicing > Reporting > Sale Report
    ''',
    'depends': ['account','sale','base_setup'],
    'data': [
        'data/service_cron_reverse.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/stock_custom_report.xml',
        'views/retail_report_config.xml',
    ],
    'installable': True,
}
