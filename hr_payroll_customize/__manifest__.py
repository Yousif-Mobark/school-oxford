# -*- coding : utf-8 -*-

{
    'name': 'Payroll Customization',
    'version': '1.0',

    'author': 'Reem Elobeid',
    'description': """
""",

    'depends': ['hr_payroll', 'hr_payroll_account'],
    'data': [
	'security/payroll_security.xml',
        'security/ir.model.access.csv',
        'data/hr_payroll_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
    ],
    'installable': True,
    'application': True,
}
