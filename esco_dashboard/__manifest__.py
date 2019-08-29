# -*- coding: utf-8 -*-
{
    'name': 'ESCO Dashboard',
    'version': '1.0',
    'category': 'Sales',
    "license": "AGPL-3", 
    'description': """
       Sales Dashboard
    """,
    'author': '',
    'website': '',
    'sequence': 1,
    'depends': ['account','sale','stock','sales_team','esco_retail_reports'],
    'data': [
            'data/service_cron_reverse.xml',
            'data/sales_dashboard_data.xml',
            'security/ir.model.access.csv',
            'security/security.xml',
            'views/sale_dashboard.xml',
            'views/res_company_inherit.xml',
            'views/retial_report_config_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: -*-
