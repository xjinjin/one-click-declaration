# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .models import DQBM_SELECTION, dict_to_xml

class ShenBaoSheet(models.Model):
    """申报表模板
    模板用来定义最终输出的 申报的报文格式,
    分地区报表类型，利用定义每个单元格的模式来实现对任何种类表格的取数和生成报文需要
    """

    _name = "cic_taxsb.shenbaosheet"
    _order = "sequence,id"
    _description = '申报表模板'

    name = fields.Char('名称')
    description = fields.Text('说明')
    sequence = fields.Integer('序号')
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', required=True, help=u'地区编码')
    tagname = fields.Char('报文标签')
    cells = fields.One2many('cic_taxsb.shenbaosheet.cell', 'sheet_id', string='单元格设置')
    template = fields.Text('模板',help='备用的模板信息')

class ShenBaoCell(models.Model):
    """申报表单元格定义模板
    模板用来定义最终输出的 申报的报文格式,
     单元格所在行号，名称，取数接口
    
    """

    _name = "cic_taxsb.shenbaosheet.cell"
    _order = "sequence,id"
    _description = u'申报表单元格模板'

    sheet_id = fields.Many2one('cic_taxsb.shenbaosheet','申报表')
    sequence = fields.Integer(u'序号')
    line = fields.Integer(u'行号', required=True, help=u'申报表的行')
    line_num = fields.Char(u'行次', help=u'此处行次并不是出报表的实际的行数,只是显示用的用来符合国人习惯')
    tagname = fields.Char('报文标签')
    get_value_func = fields.Text('取值函数', help=u'设定本单元格的取数函数代码')
    

class CreateShenbaoSheetWizard(models.TransientModel):
    """创建申报报文的向导"""
    _name = "create.shenbaosheet.wizard"
    _description = u'申报表的向导'

    
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', required=True, help='地区编码')
    sheet_id = fields.Many2one('cic_taxsb.shenbaosheet','申报表')
    account_id = fields.Many2one('cic_ocr_report.account', '账套',help='对应总账系统的账套信息')
    startdate = fields.Date('开始日期', help=u'开始日期')
    enddate = fields.Date('截止日期', help=u'截止日期')
    xml = fields.Text('XML报文')

    @api.multi
    def create_shenbao_sheet(self):
        """ 申报表的创建 """
        for record in self:
            temp_dict = {}
            for cell in record.sheet_id.cells:
                if cell.line in temp_dict:
                    key = cell.tagname
                    value = exec(cell.get_value_func, locals={})
                    if cell.line not in temp_dict:
                        temp_dict[cell.line] = {'ewbhxh': cell.line}
                    if key in temp_dict[cell.line]:
                        if isinstance(temp_dict[cell.line][key], list):
                            temp_dict[cell.line][key].append(value)
                        else:
                            temp_dict[cell.line][key] = [temp_dict[cell.line][key], value]
                    else:
                        temp_dict[cell.line][key] = value

            record.xml = dict_to_xml({record.tagname: list(temp_dict.values())})



