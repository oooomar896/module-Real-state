{
    "name": "Real Estate Management",
    "version": "1.0",
    "depends": ["base"],
    "author": "Your Name",
    "category": "Real Estate",
    "description": "Manage real estate assets, projects, and owners",
    'data': [
    'security/ir.model.access.csv',
    'views/real_estate_project_views.xml',
    'views/real_estate_owner_views.xml',
    'views/real_estate_rental_contract_views.xml',
    'views/real_estate_asset_views.xml',
    'views/real_estate_menus.xml',
],

    "installable": True,
    "application": True,
}
