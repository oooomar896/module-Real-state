{
    'name': 'إدارة عقارات ملهمة',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'نظام إدارة العقارات',
    'description': 'إدارة بيانات العقارات والملاك والمرفقات.',
    'author': 'اسمك',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'bus'],
    'data': [
        'views/property_views.xml',
        'views/contract_views.xml',
        'views/payment_views.xml',
        'views/expense_views.xml',
        'views/maintenance_views.xml',
        'views/dashboard_views.xml',
        'static/src/xml/custom_styles.xml', # <<< THIS IS IMPORTANT
        'data/ir_cron_data.xml', # Added Cron Job for contract state updates
        'data/sequence_data.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            '/estate_molhimah/static/src/css/custom_styles.css',
            '/estate_molhimah/static/src/js/custom_notification_handler.js',
            '/estate_molhimah/static/src/js/contract_form_live_update.js',
        ],
    },
}
