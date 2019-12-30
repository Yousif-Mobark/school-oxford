# -*- coding: utf-8 -*-
{
    'name': 'Read excel',
    'summary': """
       Import excel""",
    'depends': [
        'hr_attendance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/read_excel_conf_setting.xml',
        'wizard/read_excel_view.xml',
    ]
}
