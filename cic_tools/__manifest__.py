# -*- coding: utf-8 -*-
{
    'name': "cic_tools",

    'summary': """
        和嘉商通其他系统通讯的工具
    """,

    'description': """
        提供工具和嘉商通其他系统总账、园区系统和企业服务平台。
    """,

    'author': "菁涌信息",
    

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '嘉商通定制',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

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