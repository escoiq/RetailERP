# -*- coding: utf-8 -*-

{
    'name': 'Mazaj Sale Discount on Total Amount ',
    'version': '12.0.1.0.0',
    'category': 'Sales Management',
    'summary': "",
    'author': '',
    'company': '',
    'website': '',
    'description': """

""",
    'depends': ['sale',
                'account'
                ],
    'data': [
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
        'views/invoice_report.xml',
        'views/sale_order_report.xml',
        'views/res_config_view.xml',
        'views/res_company_view.xml'

    ],
    'demo': [
    ],
    'images': [],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
