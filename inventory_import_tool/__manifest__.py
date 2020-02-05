# -*- coding: utf-8 -*-
{
    'name': "Inventory Adjusment Import",

    'summary': """this module enable you to import the inventory adjustment  form excel file""",

    'description': """
        this module extend the main inventory adjustment and add excel functionality.
        """,

    'author': "Yousif Mobark",
    'website': "fb.com/yousif.mobark",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}