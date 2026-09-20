{
    'name': 'Bike Management',
    'version': '19.0.1.0.0',
    'category': 'Services',
    'summary': 'Manage bikes for Rami Bike Workshop',
    'description': """
        Bike Management for Rami Bike Workshop.

        Manage:
        - Bike name/code
        - Brand
        - Bike type
        - Purchase date
        - Last maintenance date
        - Daily rental price
        - Wheel size
    """,
    'author': 'Rami Bike Workshop',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'product',
        'portal',
    ],

    'assets': {
        'web.assets_backend': [
            'bike_management/static/src/scss/rtl.scss',
            'bike_management/static/src/scss/branding.scss',
        ],
        'web.assets_frontend': [
            'bike_management/static/src/scss/branding.scss',
        ],
    },

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/rtl_views.xml',
        'views/bike_views.xml',
        'views/repair_views.xml',
        'views/partner_views.xml',
        'data.xml',
        'report/rental_report.xml',
        'views/product_views.xml',
        'views/dashboard_views.xml',
        'views/portal_templates.xml',
        'views/rental_views.xml',
        'views/rental_analysis_views.xml',
    ],

    'application': True,
    'installable': True,
}
