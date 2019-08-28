# -*- coding: utf-8 -*-

{
    'name': 'ESCO Purchase',
    'version': '1.0',
    'author': 'Mitesh Savani',
    'category': '',
    'description': '''
        
    ''',
    'website': 'mitesh4829@gmail.com',
    'depends': ['product','purchase','account','web','product_brand'],
    'data': [
        'security/ir.model.access.csv',
#         'security/security.xml',
        'views/product_view.xml',
        'report/purchase_order_templates.xml',
        'views/purchase_view.xml',
    ],
    'installable': True,
}
