#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payroll Excel Report',
    'category': 'Human Resources',
    'sequence': 38,
    'summary': 'Manage your employee payroll excel report',
    'description': "",
    'website': 'https://www.odoo.com/page/employees',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'security/hr_report_security.xml',
        'views/hr_payroll_payslips_by_employees_views.xml',
        'views/payslip_month_report.xml',
        # 'views/hr_payroll_contribution_register_report_views.xml'
        
    ]
}
