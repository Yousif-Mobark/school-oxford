# -*- coding: utf-8 -*-
{
    'name': 'Leave Management',
    'version': '12.0.1.0.0',
    'summary': 'Manage leave Requests',
    'description': """
        Helps you to leave Loan Requests of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Reem Elobeid",
    'company': 'Reem Elobeid',
    'maintainer': 'Reem Elobeid',
    'website': "",
    'depends': [
        'base', 'hr_holidays', ],
    'data': [

        'data/hr_leave_data.xml',
	    'views/hr_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
