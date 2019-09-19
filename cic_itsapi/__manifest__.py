# -*- coding: utf-8 -*-
{
    'name': "cic_itsapi",

    'summary': """
        嘉商通个税申报接口
    """,

    'description': """
        提供工具和合力中税的个人所得税税务申报接口通讯
    """,

    'author': "菁涌信息",
    

    'category': '嘉商通定制',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}