# -*- coding: utf-8 -*-
{
    'name': "HR Contract Custom",

    'summary': """
        Inherit HR Contract to enhance search view of contracts.""",

    'description': """
        Long description of module's purpose
    """,
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}