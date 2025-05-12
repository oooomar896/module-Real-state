{
    'name': 'إدارة عقارات ملهمة',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'نظام إدارة العقارات',
    'description': 'إدارة بيانات العقارات والملاك والمرفقات.',
    'author': 'اسمك',
    'website': '',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/property_views.xml',
        'views/contract_views.xml',
        'views/payment_views.xml',
        'views/expense_views.xml',
        'views/maintenance_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        # لا تضع ملفات js أو scss أو xml هنا
    ],
    'assets': {
        'web.assets_backend': [
            'estate_molhimah/static/src/js/my_script.js',
            'estate_molhimah/static/src/scss/style.scss',
            'estate_molhimah/static/src/xml/my_template.xml',
        ],
    },
    'installable': True,
    'application': True,
}
