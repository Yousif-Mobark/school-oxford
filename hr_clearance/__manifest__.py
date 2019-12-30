# -*- coding: utf-8 -*-
{
    'name': "hr_clearance",

    'summary': """
        This module is fo the hr clearance when the employee leave the work
        """,

    'description': """
        This module is fo the hr clearance when the employee leave the work
    """,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','mail', 'product','account'],

    # always loaded
    'data': [
        'security/hr_clearance_sequerity.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'report/report_employee_clearance_template.xml',
        'report/employee_clearance_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}