# -*- coding: utf-8 -*-
{
    'name': "cic_taxsb",

    'summary': """
        嘉商通申报接口
    """,

    'description': """
        提供工具和北京中科云链信息技术有限公司的税务申报接口通讯
    """,

    'author': "菁涌信息",
    

    'category': '嘉商通定制',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail','cic_ocr_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/v2/cic_taxsb_create_uniteshenbaosheet_wizard.xml',
        'views/v2/cic_taxsb_create_json_wizard.xml',
        'views/v2/cic_taxsb_menu.xml',
        'views/v2/cic_taxsb_uniteshenbaosheet_view.xml',
        'views/v2/cic_taxsb_uniteshenbaosheet_cell_view.xml',
        'views/v2/cic_taxsb_djxx.xml',
        'views/v2/cic_taxsb_csh.xml',
        'views/v2/cic_taxsb_status.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}