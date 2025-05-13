{
    'name': 'إدارة عقارات ملهمة',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'نظام إدارة العقارات',
    'description': 'إدارة بيانات العقارات والملاك والمرفقات.',
    'author': 'اسمك',
    'website': '',
    'depends': ['base', 'web'],
    'data': [
        'views/property_views.xml',
        'views/contract_views.xml',
        'views/payment_views.xml',
        'views/expense_views.xml',
        'views/maintenance_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'estate_molhimah/static/src/css/custom_styles.css',
        ],
    },
}
