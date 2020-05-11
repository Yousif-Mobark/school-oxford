{
    'name': 'hr_penalties',
    'author': 'Osman Alrasheed',
    'website': 'http://www.google.com',
    'description': "penalties customization Module",
    'depends': ['base','mail','hr_payroll', 'account_voucher'],
    'version': '1.0',
    'data': [
        'report/penalties_report_profiel.xml',
        'report/penalties_report_template.xml',
         'security/ir.model.access.csv',
         'security/user_groups.xml',
         'views/res_setting_config_view.xml',
         'data/sequence.xml',
         'views/bonce.xml',
         'wizard/absence_deduction_wizard_views.xml',
         'views/deduction.xml',
         'views/penalties.xml',

    ],
    'installable': True,
    'auto_install': False,
}