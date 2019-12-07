# -*- coding: utf-8 -*-
# v2
from odoo import models, fields, api
from hashlib import sha256
import hmac
import base64
import uuid
import requests
import json
from math import fabs
import calendar
import os
import re

# 地区代码
DQBM_SELECTION = [
    ('11', '北京市'),
    ('12', '天津市'),
    ('13', '河北省'),
    ('14', '山西省'),
    ('15', '内蒙古区'),
    ('21', '辽宁省'),
    ('22', '吉林省'),
    ('23', '黑龙江省'),
    ('31', '上海市'),
    ('32', '江苏省'),
    ('33', '浙江省'),
    ('34', '安徽省'),
    ('35', '福建省'),
    ('36', '江西省'),
    ('37', '山东省'),
    ('41', '河南省'),
    ('42', '湖北省'),
    ('43', '湖南省'),
    ('44', '广东省'),
    ('45', '广西区'),
    ('46', '海南省'),
    ('50', '重庆市'),
    ('51', '四川省'),
    ('52', '贵州省'),
    ('53', '云南省'),
    ('54', '西藏区'),
    ('61', '陕西省'),
    ('62', '甘肃省'),
    ('63', '青海省'),
    ('64', '宁夏区'),
    ('65', '新疆区'),
    ('2102', '大连市'),
    ('3302', '宁波市'),
    ('3502', '厦门市'),
    ('3702', '青岛市'),
    ('4403', '深圳市'),
]

# 纳税人资格代码
NSRZGDM_SELECTION = [
    ('001', '增值税一般纳税人'),
    ('101', '增值税小规模纳税人'),
]

# 登陆方式（1.用户名/密码 2.ca登陆）
DLFS_SELECTION = [
    ('1', 'CA登录'),
    ('2', '密码登录'),
    ('3', '实名账号'),
]

# 税种代码表
SZDM_SELECTION = [
    ('10101', '增值税一般纳税人申报表'),
    ('10102', '增值税小规模申报表'),
    ('10516', '城建税、教育费附加、地方教育附加税(费)申报表(月)'),
    ('B0516', '城建税、教育费附加、地方教育附加税(费)申报表(季)'),
    ('10502', '城镇土地使用税纳税申报表'),
    ('10520', '地方各项基金费申报表（月报）'),
    ('B0520', '地方各项基金费申报表（季）'),
    ('10501', '房产税纳税申报表'),
    ('90201', '综合所得申报表'),
    ('10512', '分类所得申报表'),
    ('10513', '非居民所得申报表'),
    ('10524', '个人经营所得A类'),
    ('10412', '企业所得税月（季）报A类'),
    ('10413', '企业所得税月（季）报B类'),
    ('90106', '社会保险费缴纳表'),
    ('10601', '文化事业建设费(新国税)'),
    ('39805', '财务报表(企业会计制度)'),
    ('29806', '财务报表(小企业会计准则)'),
    ('10311', '消费税（电池）申报表'),
    ('10111', '印花税纳税申报表(新)月/季'),
    ('B0111', '印花税纳税申报表(选报)次'),
    ('B9805', '财务报表(企业会计准则)'),
    ('C0502', '财务报表(企业会计准则)'),
    ('90601', '生产经营所得纳税申报表'),
    ('10306', '消费税其他'),
    ('42016', '增值税预缴申报'),
    ('10521', '土地增值税纳税申报表'),
    ('10517', '残疾人就业保障金缴费申报表 月'),
    ('B0517', '残疾人就业保障金缴费申报表 季'),
]



# serviceId代码表
SERVICEID_SELECTION = [
    ('42016', '[42016]增值税预缴税'),
    ('10101', '[10101]增值税一般纳税人'),
    ('10102', '[10102]增值税小规模纳税人'),
    ('B0516', '[B0516]城建税、教育费附加、地方教育附加税(季)(费)'),
    ('10516', '[10516]城建税、教育费附加、地方教育附加税(月)(费)'),
    ('10521', '[10521]土地增值税预征'),
    ('10502', '[10502]城镇土地使用税'),
    ('10501', '[10501]房产税'),
    ('10520', '[10520]地方各项基金费税(月报)'),
    ('C0502', '[C0502]地方各项基金费税(选报)基金'),
    ('B0520', '[B0520]地方各项基金费税(季度)'),
    ('10517', '[10517]残疾人保障基金'),
    ('10601', '[10601]文化事业建设费(新国税)'),
    ('10111', '[10111]印花税(月)'),
    ('B0111', '[B0111]印花税(次)'),
    ('90106', '[90106]社会保险费缴纳税'),
    ('10350', '[10350]消费税(其他)'),
    ('10311', '[10311]消费税(电池)'),
    ('10413', '[10413]企业所得税月(季)报B类'),
    ('10412', '[10412]企业所得税月(季)报A类'),
    ('B9805', '[B9805]财务报表(企业会计准则)'),
    ('39805', '[39805]财务报表(企业会计制度)'),
    ('29806', '[29806]财务报表(小企业会计准则)'),
    ('10524', '[10524]个人经营所得A类'),
    ('90601', '[90601]生产经营所得纳税'),
    ('10512', '[10512]分类所得税'),
    ('90201', '[90201]综合所得税'),
    ('10513', '[10513]非居民所得税')
]

# 纳税期限代码
NSQXDM_SELECTION = [
    ('02', '月度'),
    ('03', '季度'),
    ('05', '半年度'),
    ('04', '年度'),
    ('01', '按次'),
]

# 重新获取标志
CXHQBZ_SELECTION = [
    ('0', '直接获取结果'),
    ('1', '重新发起请求')
]

# 配偶标志
POBZ_SELECTION = [
    ('0', '无'),
    ('1', '有')
]

# 独生子女标志
DSZNBZ_SELECTION = [
    ('0', '否'),
    ('1', '是')
]

# 本人借款标志 0-否 1-是
BRJKBZ_SELECTION = [
    ('0', '否'),
    ('1', '是')
]

# 贷款类型 1-公积金贷款 2-商业贷款
DKLX_SELECTION = [
    ('1', '公积金贷款'),
    ('2', '商业贷款')
]

# 会计制度代码
KJZDDM_SELECTION = [
    ('1', '小企业会计准则2013版'),
    ('2', '企业会计制度'),
    ('3', '企业会计准则2007版'),
    ('4', '企业会计准则2017版'),
    ('5', '企业会计准则2017版'),
    ('6', '企业会计准则(商业银行)'),
    ('7', '企业会计准则(保险公司)'),
    ('8', '企业会计准则(证券公司)'),
    ('9', '企业会计准则(担保企业快捷核算办法)')
]

# 企业身份代码
QYSFDM_SELECTION = [
    ('001', '增值税一般纳税人'),
    ('101', '增值税小规模纳税人')
]

# 申报初始化接口返回代码
SBCSHJKFHDM_SELECTION = [
    ('B1000', '初始化成功'),
    ('B2000', '初始化失败')
]

# 申报提交接口状态代码
SBTJJKZTDM_SELECTION = [
    ('B0000', '受理中'),
    ('B1000', '受理成功'),
    ('B2000', '受理中')
]

# 申报结果查询代码
SBJGCXDM_SELECTION = [
    ('S0000', '未申报'),
    ('S1000', '申报成功'),
    ('S2000', '申报失败'),
    ('B1000', '申报中')
]

# 申报作废结果返回代码
SBZFJGFHDM_SELECTION = [
    ('Z0000', '作废成功'),
    ('Z1000', '作废失败')
]

class taxsbBase(models.Model):
    _name = "cic_taxsb.base"
    _description = "嘉商通总账系统申报接口API基础类"

    host = fields.Char('主机', default='180.168.162.219')
    port = fields.Integer('端口', default=8004)
    path = fields.Char('接口地址', default='remote/callServer')

    appkey = fields.Char('appKey', default="922f00cd5f2e4c1198934edd4de54778")
    token = fields.Char('token', default="10fb04a95c8e75259fb1a50e")
    lsh = fields.Char(string='流水号,用于此次请求的业务追踪', help="流水号,用于此次请求的业务追踪")

    @api.multi
    def create_lsh(self):
        for record in self:
            record.lsh = uuid.uuid4()

    @api.one
    def post(self):
        url = "http://{}:{}/{}".format(self.host, self.port, self.path)
        params = {
            "appKey": self.appkey,
            "token": hmac.new(bytes(self.token, 'utf-8'), msg=bytes(self.content, 'utf-8'), digestmod=sha256).hexdigest(),
            "serviceId": self.serviceId,
            "lsh": self.lsh,
            "jsonData": self.content
        }
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        res = requests.post(url, data=params, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            return res.text

class SBDjxx(models.Model):
    _name = "cic_taxsb.djxx"
    _description = "登记税号基本信息"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号 必须传")
    qymc = fields.Char('企业名称', help="企业名称 必须传")
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', help="地区编码【参考地区编码 平台申报开放API规范2.0(1)文档】 必须传")
    cwlxr = fields.Char('财务联系人', help="财务联系人          【江苏必须传】")
    cwlxrlxfs = fields.Char('财务联系人联系电话', help="财务联系人联系电话  【江苏必须传】")
    dscsdlmm = fields.Char('地税CA密码', help="地税CA密码 目前不支持")
    dsdlfs = fields.Selection(DLFS_SELECTION, string='地税登录方式', default='2',
                              help="地税登录方式 1 CA(目前不支持线上，需要联系运维人员) 2 用户名密码")
    dsdlmm = fields.Char('地税登录密码', help="地税登录密码")
    dsdlyhm = fields.Char('地税登录名', help="地税登录名")
    gscamm = fields.Char('国税CA密码', help="国税CA密码【(目前不支持线上，需要联系运维人员) 】")
    gsdlfs = fields.Selection(DLFS_SELECTION, string='国税登录方式', default='2',
                              help="国税登录方式 【1: CA(目前不支持线上，需要联系运维人员) 2: 用户名密码(税号)  3:实名账号(江苏无需此类型) 】")
    gsnsmm = fields.Char('国税登录密码', help="国税登录密码                      必须传")
    gsnsrsbh = fields.Char('国税纳税人识别号', help="纳税人识别号        必须传")
    gsnsyhm = fields.Char('国税登录名', help="国税登录名            必须传")
    kjzd = fields.Char(KJZDDM_SELECTION, string='会计制度,必须传', default='1', help="会计制度,必须传")
    nsrzgdm = fields.Selection(NSRZGDM_SELECTION, string='nsrzgdm', help="纳税资格代码 【001增值税一般纳税人/101增值税小规模纳税人】 必须传")
    qyyf = fields.Char('月份', help="启用月份(必填) 【系统(当前)月份】          必须传")
    qynf = fields.Char('年份', help="启用年份(必填) 【系统(当前)年份】          必须传")

    serviceId = fields.Char('服务方法标识', default='S001', help="服务方法标识")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh',
            'qymc',
            'dqbm',
            'cwlxr',
            'cwlxrlxfs',
            'dscsdlmm',
            'dsdlfs',
            'dsdlmm',
            'dsdlyhm',
            'gscamm',
            'gsdlfs',
            'gsnsmm',
            'gsnsrsbh',
            'gsnsyhm',
            'kjzd',
            'nsrzgdm',
            'qyyf',
            'qynf'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]  # {'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}
            # temp_dict = record.read(_fields)  # [{'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}]
            temp_dict.pop('id', None)  # {'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}
            record.content = json.dumps(temp_dict)

class SBInit(models.Model):
    _name = "cic_taxsb.csh"
    _description = "申报初始化接口,获取对应税种的初始化信息"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码',  help="参考代码表")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码',  help="参考代码表")
    skssqq = fields.Char('税款所属期起,格式yyyy-MM-dd', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止,格式yyyy-MM-dd', help="税款所属期止:('2019-08-31')")
    isRenew = fields.Char(CXHQBZ_SELECTION,string='重新获取标志',default='0', help="重新获取标志")

    serviceId = fields.Char('服务方法标识', default='S002', help="服务方法标识")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh',
            'sbzlbh',
            'nsqxdm',
            'skssqq',
            'skssqz',
            'isRenew'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)

class SBStatus(models.Model):
    _name = "cic_taxsb.status"
    _description = "申报状态查询接口,用于申报提交之后的状态查询,该接口也支持作废、缴款的状态查询"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号 必须传")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码',  help="参考代码表")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', help="参考代码表")
    skssqq = fields.Char('税款所属期起,格式yyyy-MM-dd', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止,格式yyyy-MM-dd', help="税款所属期止:('2019-08-31')")

    serviceId = fields.Char('服务方法标识', default='S004', help="服务方法标识")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh',
            'sbzlbh',
            'nsqxdm',
            'skssqq',
            'skssqz'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)

cell_stable_value = ['lmc', 'ewblxh', 'ewbhxh', 'hmc', 'xmmc', 'lc', 'jmxzdmjmc', 'msxmdmjmc', 'zcxmmc', 'zsxmMc',
                     'zspmMc', 'zsxmDm', 'zspmDm', 'xm']
class SBSubmitWizard(models.TransientModel):
    """
    申报提交接口,用于客户提交申报请求报文
    根据统一报文对象，创建统一报文格式
    """
    _name = "cic_taxsb.submit.wizard"
    _description = '申报提交向导'
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', help="参考代码表")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码',help="参考代码表")
    skssqq = fields.Char('所属期起 yyyy-MM-dd', help='所属期起 yyyy-MM-dd')
    skssqz = fields.Char('所属期止 yyyy-MM-dd', help='所属期止 yyyy-MM-dd')

    sheet_id = fields.Many2one('cic_taxsb.uniteshenbaosheet', '申报表', required=True)
    account_id = fields.Many2one('cic_ocr_report.account', '账套', help='对应总账系统的账套信息')

    serviceId = fields.Char('服务方法标识', default='S003', help="服务方法标识")

    create_dict = fields.Text('统一报文')
    content = fields.Text('报文内容', compute='_compute_content')

    # {'sheet_id': 44,'account_id': 100, 'startdate': '2019-09-01', 'enddate': '2019-09-30'}
    # {'nsrsbh': '91320214MA1NYKMBXK', 'nsqxdm': '1','skssqz': '2019-07-01', 'sbzlbh': '29806'}
    # {'appkey': '3ccb2aab00e149eab2b9567fbf508217', 'token': '515d582419d2ee937d2f8084'}

    @api.multi
    def _compute_content(self):

        _fields = [
            'nsrsbh',
            'sbzlbh',
            'nsqxdm',
            'skssqq',
            'skssqz'
        ]
        for record in self:
            if not record.ujson:
                temp_dict = record.read(_fields)[0]  # {'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}
                # temp_dict = record.read(_fields)  # [{'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}]
                temp_dict.pop('id', None)  # {'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}
                content = json.dumps(record.ujson)
                temp_dict['bizXml'] = base64.b64encode(content.encode('utf-8')).decode("utf-8")
                record.content = json.dumps(temp_dict)

    @api.multi
    def create_uniteshenbao_sheet(self):
        '''根据统一报文对象，创建统一报文格式. dict'''
        for record in self:
            # res = record.env['cic_tools.cic_finance'].get_declaration_data(record.account_id.levyNum, record.startdate,record.enddate)
            # res = record.env['cic_tools.cic_finance'].get_declaration_data('91320214MA1NYKMBXK','2019-07-01','2019-09-30')

            level_two_dict = {}
            # 构造level_two_dict
            for level_two_obj in record.sheet_id.child_ids:
                # 判断2层对象是否有cells
                if not level_two_obj.cells:
                    # 2层对象没有cells
                    level_three_dict = {}
                    for level_three_obj in level_two_obj.child_ids:
                        # 判断3层对象是否有cells
                        if not level_three_obj.cells:
                            # 3层对象没有cells
                            level_four_dict = {}
                            for level_four_obj in level_three_obj.child_ids:
                                # 构建第四层字典   # 第5层的字典：单元格，字典，单元格+列表
                                if not level_four_obj.cells:
                                    # 4层对象：字典：只有表没有单元格
                                    level_five_dict = {}  # 构建第五层，分几种情况：列表和字典
                                    level_five_list = []  # cgwgqyxxbgbVO
                                    level_four_value_list = ['cgwgqyxxbgbVO']
                                    # 5层对象没有cells
                                    # {"cgwgqyxxbgbVO":[{"gdxxGrid": {"gdxxGridlb":[{...},...]},"wgqyxxForm":{...}}]}
                                    if level_four_obj.tagname in level_four_value_list:
                                        level_six_dict = {}
                                        for level_five_obj in level_four_obj.child_ids:
                                            if not level_five_obj.cells:
                                                level_seven_dict = {}  # 构建第7层字典
                                                level_nine_dict = {}
                                                for level_six_obj in level_five_obj.child_ids:
                                                    for cell in level_six_obj.cells:
                                                        key = cell.tagname
                                                        # exec(cell.get_value_func,{'res':res,'cell':cell})
                                                        # value = cell.value
                                                        value = '110'
                                                        if str(cell.line) not in level_nine_dict:
                                                            level_nine_dict[str(cell.line)] = {}
                                                            level_nine_dict[str(cell.line)][key] = value
                                                        else:
                                                            level_nine_dict[str(cell.line)][key] = value
                                                    level_seven_dict[level_six_obj.tagname] = list(
                                                        level_nine_dict.values())
                                                level_six_dict[level_five_obj.tagname] = level_seven_dict
                                            else:
                                                level_seven_dict = {}
                                                for cell in level_five_obj.cells:
                                                    key = cell.tagname
                                                    # exec(cell.get_value_func,{'res':res,'cell':cell})
                                                    # value = cell.value
                                                    value = '110'
                                                    level_seven_dict[key] = value
                                                level_six_dict[level_five_obj.tagname] = level_seven_dict
                                        level_five_list.append(level_six_dict)
                                    else:
                                        for level_five_obj in level_four_obj.child_ids:
                                            # if not level_five_obj.cells:
                                            #     pass
                                            # else:
                                            level_six_dict = {}
                                            level_seven_dict = {}
                                            for cell in level_five_obj.cells:
                                                key = cell.tagname
                                                # exec(cell.get_value_func,{'res':res,'cell':cell})
                                                # value = cell.value
                                                value = '110'
                                                if not cell.line:  # 单元格是否带行号，不带行号:dict
                                                    level_six_dict[key] = value
                                                else:  # 带行号:list
                                                    if str(cell.line) not in level_seven_dict:
                                                        level_seven_dict[str(cell.line)] = {}
                                                        if cell.value:
                                                            level_seven_dict[str(cell.line)][key] = cell.value
                                                        else:
                                                            level_seven_dict[str(cell.line)][key] = value
                                                    else:
                                                        if cell.value:
                                                            level_seven_dict[str(cell.line)][key] = cell.value
                                                        else:
                                                            level_seven_dict[str(cell.line)][key] = value
                                            if level_six_dict:
                                                level_five_dict[level_five_obj.tagname] = level_six_dict
                                            if level_seven_dict:
                                                level_five_dict[level_five_obj.tagname] = list(
                                                    level_seven_dict.values())
                                    level_four_dict[level_four_obj.tagname] = level_five_dict or level_five_list
                                else:
                                    # 4层对象：单元格，单元格+列表。构建5层字典
                                    level_five_dict = {}  # 构建5层字典
                                    if level_four_obj.child_ids:  # 有表
                                        for level_five_obj in level_four_obj.child_ids:
                                            level_seven_dict = {}
                                            for cell in level_five_obj.cells:
                                                key = cell.tagname
                                                # exec(cell.get_value_func,{'res':res,'cell':cell})
                                                # value = cell.value
                                                value = '110'
                                                if not cell.line:  # 单元格是否带行号，不带行号:dkdjsstyjksdkqdGridlb
                                                    level_seven_dict[key] = value
                                                else:  # 带行号:hznsqyzzsfpbGridlbVO
                                                    if str(cell.line) not in level_seven_dict:
                                                        level_seven_dict[str(cell.line)] = {}
                                                        if cell.value:
                                                            level_seven_dict[str(cell.line)][key] = cell.value
                                                        else:
                                                            level_seven_dict[str(cell.line)][key] = value
                                                    else:
                                                        if cell.value:
                                                            level_seven_dict[str(cell.line)][key] = cell.value
                                                        else:
                                                            level_seven_dict[str(cell.line)][key] = value

                                            if isinstance(list(level_seven_dict.values())[0], dict):
                                                level_five_dict[level_five_obj.tagname] = list(
                                                    level_seven_dict.values())
                                            else:
                                                level_five_dict[level_five_obj.tagname] = [level_seven_dict]
                                    for cell in level_four_obj.cells:  # 纯单元格
                                        if cell.value:
                                            level_five_dict[cell.tagname] = cell.value
                                        else:
                                            # exec(cell.get_value_func,{'res':res,'cell':cell})
                                            # value = cell.value
                                            value = '110'
                                            level_five_dict[cell.tagname] = value
                                    if level_four_obj.tagname == 'kcxmqdmx':
                                        level_four_dict[level_four_obj.tagname] = [level_five_dict]
                                    else:
                                        level_four_dict[level_four_obj.tagname] = level_five_dict
                            level_three_dict[level_three_obj.tagname] = level_four_dict
                        else:
                            # 3层对象有cells
                            level_four_dict = {}
                            for cell in level_three_obj.cells:
                                if cell.value:
                                    level_four_dict[cell.tagname] = cell.value
                                else:
                                    # exec(cell.get_value_func,{'res':res,'cell':cell})
                                    # value = cell.value
                                    value = '110'
                                    level_four_dict[cell.tagname] = value
                            level_three_dict[level_three_obj.tagname] = level_four_dict
                    level_two_dict[level_two_obj.tagname] = level_three_dict
                else:
                    # 2层对象有cells
                    level_three_dict = {}
                    for cell in level_two_obj.cells:
                        if cell.value:
                            level_three_dict[cell.tagname] = cell.value
                        else:
                            # exec(cell.get_value_func,{'res':res,'cell':cell})
                            # value = cell.value
                            value = '110'
                            level_three_dict[cell.tagname] = value
                    level_two_dict[level_two_obj.tagname] = level_three_dict

            level_one_dict = {record.sheet_id.tagname: level_two_dict}
            record.create_dict = level_one_dict

comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)
class UniteCreateJsonObjWizard(models.TransientModel):
    """上传统一报文json文件，创建统一报文对象（自动增加项暂未考虑）"""
    _name = "unite.create.json.obj.wizard"
    _description = '创建json的向导'

    name = fields.Char(string='json统一报文', help='附加税交付报文_V20191015.json')
    file = fields.Binary(string="Upload Json File")

    @api.one
    def create_json_obj(self):
        # bytes--->str
        content = base64.b64decode(self.file).decode('utf-8')
        # 清除注释
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)
        # 字典
        content_dict = eval(content)

        file_name_no_extend, extension_name = os.path.splitext(self.name)
        shenbaosheetcell = self.env['cic_taxsb.uniteshenbaosheet.cell']
        shenbaosheet = self.env['cic_taxsb.uniteshenbaosheet']

        level_one_keys = list(content_dict.keys())

        # 判断第一层的情况：1.单个key（大部分情况） 2.多个key（统一报文，财务报表）
        # 对于第二种情况，在第一层之上在加一层，解决创建报文结构时sheet_id的问题。
        if len(level_one_keys) >= 2:
            # 创建抽象0层的对象
            level_zero_key_obj = shenbaosheet.create({'name': file_name_no_extend, 'tagname': 'level_zero_key'})
            level_zero_key_id = level_zero_key_obj.id

            # 创建第一层keys
            for level_one_key in level_one_keys:
                level_one_key_obj = shenbaosheet.create({'parent_id': level_zero_key_id, 'tagname': level_one_key})
                level_one_key_id = level_one_key_obj.id

                # 创建第二层keys
                level_two_dict = content_dict[level_one_key]
                level_two_keys = list(level_two_dict.keys())
                for level_two_key in level_two_keys:
                    level_two_key_obj = shenbaosheet.create({'parent_id': level_one_key_id, 'tagname': level_two_key})
                    level_two_key_id = level_two_key_obj.id

                    # # 统一报文财务报表：第二层的values是list
                    # if isinstance(level_two_dict[level_two_key],list):
                    #     level_three_list = level_two_dict[level_two_key]
                    #     line = 0
                    #     for level_four_dict in level_three_list:
                    #         line = line + 1
                    #         for level_four_key in list(level_four_dict.keys()):
                    #             shenbaosheetcell.create({'sheet_id': level_two_key_id, 'tagname': level_four_key, 'line': line})

                    # 第三层的values分类：     1.dict      2.cell
                    # 创建第三层的keys
                    level_three_dict = level_two_dict[level_two_key]
                    if isinstance(list(level_three_dict.values())[0], dict):
                        level_three_keys = list(level_three_dict.keys())
                        for level_three_key in level_three_keys:
                            level_three_key_obj = shenbaosheet.create(
                                {'parent_id': level_two_key_id, 'tagname': level_three_key})
                            level_three_key_id = level_three_key_obj.id

                            # 第四层的的values分类:    1.cell  2.dict  3.list
                            # 创建第四层的keys
                            level_four_dict = level_three_dict[level_three_key]
                            level_four_keys = list(level_four_dict.keys())
                            if isinstance(list(level_four_dict.values())[0], dict):
                                for level_four_key in level_four_keys:
                                    level_four_key_obj = shenbaosheet.create(
                                        {'parent_id': level_three_key_id, 'tagname': level_four_key})
                                    level_four_key_id = level_four_key_obj.id

                                    # 第五层的的values分类:    1.list  2.dict  3.cell
                                    # 创建第五层的keys
                                    level_five_dict = level_four_dict[level_four_key]
                                    level_five_keys = list(level_five_dict.keys())
                                    for level_five_key in level_five_keys:
                                        if isinstance(level_five_dict[level_five_key], list):
                                            level_five_key_obj = shenbaosheet.create(
                                                {'parent_id': level_four_key_id, 'tagname': level_five_key})
                                            level_five_key_id = level_five_key_obj.id

                                            level_six_list = level_five_dict[level_five_key]
                                            line_no = 0
                                            for level_seven_dict in level_six_list:
                                                level_seven_keys = list(level_seven_dict.keys())
                                                if 'ewbhxh' in level_seven_dict or 'ewblxh' in level_seven_dict:
                                                    if level_seven_dict.get('ewbhxh') == '合计':
                                                        line = 999
                                                    else:
                                                        line = int(level_seven_dict.get('ewbhxh', 0)) or int(
                                                            level_seven_dict.get('ewblxh', 0))
                                                    for level_seven_key in level_seven_keys:
                                                        if level_seven_key in cell_stable_value:
                                                            shenbaosheetcell.create(
                                                                {'sheet_id': level_five_key_id,
                                                                 'tagname': level_seven_key,
                                                                 'line': line,
                                                                 'value': level_seven_dict[level_seven_key]})
                                                        else:
                                                            shenbaosheetcell.create(
                                                                {'sheet_id': level_five_key_id,
                                                                 'tagname': level_seven_key,
                                                                 'line': line})
                                                else:
                                                    line_no = line_no + 1
                                                    for level_seven_key in level_seven_keys:
                                                        shenbaosheetcell.create(
                                                            {'sheet_id': level_five_key_id, 'tagname': level_seven_key,
                                                             'line': line_no})
                                        # 第五层的的values分类:  2.dict
                                        elif isinstance(level_five_dict[level_five_key], dict):
                                            level_five_key_obj = shenbaosheet.create(
                                                {'parent_id': level_four_key_id, 'tagname': level_five_key})
                                            level_five_key_id = level_five_key_obj.id
                                            # 创建第六层的单元格
                                            level_six_dict = level_five_dict[level_five_key]
                                            level_six_keys = list(level_six_dict.keys())
                                            for level_six_key in level_six_keys:
                                                shenbaosheetcell.create({'sheet_id': level_five_key_id,
                                                                         'tagname': level_six_key})  # line value get_value_func
                                        # 第五层的的values分类:    3.cell
                                        else:
                                            shenbaosheetcell.create({'sheet_id': level_four_key_id,
                                                                     'tagname': level_five_key})  # line value get_value_func

                            # 第四层的的values分类:    3.list
                            # 创建第四层的keys，创建单元格
                            elif isinstance(list(level_four_dict.values())[0], list):
                                for level_four_key in level_four_keys:
                                    level_four_key_obj = shenbaosheet.create(
                                        {'parent_id': level_three_key_id, 'tagname': level_four_key})
                                    level_four_key_id = level_four_key_obj.id

                                    level_five_list_dict = level_four_dict[level_four_key][0]
                                    level_five_list_dict_keys = list(level_five_list_dict.keys())
                                    for level_five_list_dict_key in level_five_list_dict_keys:
                                        if isinstance(level_five_list_dict[level_five_list_dict_key], dict):
                                            level_five_list_dict_key_obj = shenbaosheet.create(
                                                {'parent_id': level_four_key_id, 'tagname': level_five_list_dict_key})
                                            level_five_list_dict_key_id = level_five_list_dict_key_obj.id

                                            level_seven_dict = level_five_list_dict[level_five_list_dict_key]
                                            level_seven_dict_keys = list(level_seven_dict.keys())
                                            for level_seven_dict_key in level_seven_dict_keys:
                                                if isinstance(level_seven_dict[level_seven_dict_key], list):
                                                    level_seven_dict_key_obj = shenbaosheet.create(
                                                        {'parent_id': level_five_list_dict_key_id,
                                                         'tagname': level_seven_dict_key})
                                                    level_seven_dict_key_id = level_seven_dict_key_obj.id

                                                    level_eight_list = level_seven_dict[level_seven_dict_key]
                                                    line_level_nine = 0
                                                    for level_nine_dict in level_eight_list:
                                                        line_level_nine = line_level_nine + 1
                                                        level_nine_keys_list = list(level_nine_dict.keys())
                                                        for level_nine_key in level_nine_keys_list:
                                                            shenbaosheetcell.create(
                                                                {'sheet_id': level_seven_dict_key_id,
                                                                 'tagname': level_nine_key,
                                                                 'line': line_level_nine})
                                                else:
                                                    shenbaosheetcell.create({'sheet_id': level_five_list_dict_key_id,
                                                                             'tagname': level_seven_dict_key})
                                        else:
                                            shenbaosheetcell.create({'sheet_id': level_four_key_id,
                                                                     'tagname': level_five_list_dict_key})  # line value get_value_func

                            # 第四层的的values分类:    1.cell  创建单元格
                            else:
                                for level_four_key in level_four_keys:
                                    shenbaosheetcell.create({'sheet_id': level_three_key_id,
                                                             'tagname': level_four_key})  # line value get_value_func

                    # 第三层的values分类： 2.cell   创建单元格 固定值写入value
                    else:
                        level_three_keys = list(level_three_dict.keys())
                        for level_three_key in level_three_keys:
                            if level_three_key == 'sz':
                                shenbaosheetcell.create({'sheet_id': level_two_key_id, 'tagname': level_three_key,
                                                         'value': level_three_dict['sz']})
                            else:
                                shenbaosheetcell.create(
                                    {'sheet_id': level_two_key_id,
                                     'tagname': level_three_key})  # line value get_value_func
        else:

            # 创建第一层keys
            # level_one_key = list(content_dict.keys())[0]
            level_one_key = level_one_keys[0]
            # for level_one_key in level_one_keys:
            level_one_key_obj = shenbaosheet.create({'name': file_name_no_extend, 'tagname': level_one_key})
            level_one_key_id = level_one_key_obj.id

            # 创建第二层keys
            level_two_dict = content_dict[level_one_key]
            level_two_keys = list(level_two_dict.keys())
            for level_two_key in level_two_keys:
                level_two_key_obj = shenbaosheet.create({'parent_id': level_one_key_id, 'tagname': level_two_key})
                level_two_key_id = level_two_key_obj.id

                # # 统一报文财务报表：第二层的values是list
                # if isinstance(level_two_dict[level_two_key],list):
                #     level_three_list = level_two_dict[level_two_key]
                #     line = 0
                #     for level_four_dict in level_three_list:
                #         line = line + 1
                #         for level_four_key in list(level_four_dict.keys()):
                #             shenbaosheetcell.create({'sheet_id': level_two_key_id, 'tagname': level_four_key, 'line': line})

                # 第三层的values分类：     1.dict      2.cell
                # 创建第三层的keys
                level_three_dict = level_two_dict[level_two_key]
                if isinstance(list(level_three_dict.values())[0], dict):
                    level_three_keys = list(level_three_dict.keys())
                    for level_three_key in level_three_keys:
                        level_three_key_obj = shenbaosheet.create(
                            {'parent_id': level_two_key_id, 'tagname': level_three_key})
                        level_three_key_id = level_three_key_obj.id

                        # 第四层的的values分类:    1.cell  2.dict  3.list
                        # 创建第四层的keys
                        level_four_dict = level_three_dict[level_three_key]
                        level_four_keys = list(level_four_dict.keys())
                        if isinstance(list(level_four_dict.values())[0], dict):
                            for level_four_key in level_four_keys:
                                level_four_key_obj = shenbaosheet.create(
                                    {'parent_id': level_three_key_id, 'tagname': level_four_key})
                                level_four_key_id = level_four_key_obj.id

                                # 第五层的的values分类:    1.list  2.dict  3.cell
                                # 创建第五层的keys
                                level_five_dict = level_four_dict[level_four_key]
                                level_five_keys = list(level_five_dict.keys())
                                for level_five_key in level_five_keys:
                                    if isinstance(level_five_dict[level_five_key], list):
                                        level_five_key_obj = shenbaosheet.create(
                                            {'parent_id': level_four_key_id, 'tagname': level_five_key})
                                        level_five_key_id = level_five_key_obj.id

                                        level_six_list = level_five_dict[level_five_key]
                                        line_no = 0
                                        for level_seven_dict in level_six_list:
                                            level_seven_keys = list(level_seven_dict.keys())
                                            if 'ewbhxh' in level_seven_dict or 'ewblxh' in level_seven_dict:
                                                if level_seven_dict.get('ewbhxh') == '合计':
                                                    line = 999
                                                else:
                                                    line = int(level_seven_dict.get('ewbhxh', 0)) or int(
                                                        level_seven_dict.get('ewblxh', 0))
                                                for level_seven_key in level_seven_keys:
                                                    if level_seven_key in cell_stable_value:
                                                        shenbaosheetcell.create(
                                                            {'sheet_id': level_five_key_id, 'tagname': level_seven_key,
                                                             'line': line, 'value': level_seven_dict[level_seven_key]})
                                                    else:
                                                        shenbaosheetcell.create(
                                                            {'sheet_id': level_five_key_id, 'tagname': level_seven_key,
                                                             'line': line})
                                            else:
                                                line_no = line_no + 1
                                                for level_seven_key in level_seven_keys:
                                                    shenbaosheetcell.create(
                                                        {'sheet_id': level_five_key_id, 'tagname': level_seven_key,
                                                         'line': line_no})
                                    # 第五层的的values分类:  2.dict
                                    elif isinstance(level_five_dict[level_five_key], dict):
                                        level_five_key_obj = shenbaosheet.create(
                                            {'parent_id': level_four_key_id, 'tagname': level_five_key})
                                        level_five_key_id = level_five_key_obj.id
                                        # 创建第六层的单元格
                                        level_six_dict = level_five_dict[level_five_key]
                                        level_six_keys = list(level_six_dict.keys())
                                        for level_six_key in level_six_keys:
                                            shenbaosheetcell.create({'sheet_id': level_five_key_id,
                                                                     'tagname': level_six_key})  # line value get_value_func
                                    # 第五层的的values分类:    3.cell
                                    else:
                                        shenbaosheetcell.create({'sheet_id': level_four_key_id,
                                                                 'tagname': level_five_key})  # line value get_value_func

                        # 第四层的的values分类:    3.list
                        # 创建第四层的keys，创建单元格
                        elif isinstance(list(level_four_dict.values())[0], list):
                            for level_four_key in level_four_keys:
                                level_four_key_obj = shenbaosheet.create(
                                    {'parent_id': level_three_key_id, 'tagname': level_four_key})
                                level_four_key_id = level_four_key_obj.id

                                level_five_list_dict = level_four_dict[level_four_key][0]
                                level_five_list_dict_keys = list(level_five_list_dict.keys())
                                for level_five_list_dict_key in level_five_list_dict_keys:
                                    if isinstance(level_five_list_dict[level_five_list_dict_key], dict):
                                        level_five_list_dict_key_obj = shenbaosheet.create(
                                            {'parent_id': level_four_key_id, 'tagname': level_five_list_dict_key})
                                        level_five_list_dict_key_id = level_five_list_dict_key_obj.id

                                        level_seven_dict = level_five_list_dict[level_five_list_dict_key]
                                        level_seven_dict_keys = list(level_seven_dict.keys())
                                        for level_seven_dict_key in level_seven_dict_keys:
                                            if isinstance(level_seven_dict[level_seven_dict_key], list):
                                                level_seven_dict_key_obj = shenbaosheet.create(
                                                    {'parent_id': level_five_list_dict_key_id,
                                                     'tagname': level_seven_dict_key})
                                                level_seven_dict_key_id = level_seven_dict_key_obj.id

                                                level_eight_list = level_seven_dict[level_seven_dict_key]
                                                line_level_nine = 0
                                                for level_nine_dict in level_eight_list:
                                                    line_level_nine = line_level_nine + 1
                                                    level_nine_keys_list = list(level_nine_dict.keys())
                                                    for level_nine_key in level_nine_keys_list:
                                                        shenbaosheetcell.create({'sheet_id': level_seven_dict_key_id,
                                                                                 'tagname': level_nine_key,
                                                                                 'line': line_level_nine})
                                            else:
                                                shenbaosheetcell.create({'sheet_id': level_five_list_dict_key_id,
                                                                         'tagname': level_seven_dict_key})
                                    else:
                                        shenbaosheetcell.create({'sheet_id': level_four_key_id,
                                                                 'tagname': level_five_list_dict_key})  # line value get_value_func

                        # 第四层的的values分类:    1.cell  创建单元格
                        else:
                            for level_four_key in level_four_keys:
                                shenbaosheetcell.create({'sheet_id': level_three_key_id,
                                                         'tagname': level_four_key})  # line value get_value_func

                # 第三层的values分类： 2.cell   创建单元格 固定值写入value
                else:
                    level_three_keys = list(level_three_dict.keys())
                    for level_three_key in level_three_keys:
                        if level_three_key == 'sz':
                            shenbaosheetcell.create({'sheet_id': level_two_key_id, 'tagname': level_three_key,
                                                     'value': level_three_dict['sz']})
                        else:
                            shenbaosheetcell.create(
                                {'sheet_id': level_two_key_id, 'tagname': level_three_key})  # line value get_value_func

class UniteShenBaoSheet(models.Model):
    """统一申报表模板
    模板用来定义最终输出的 申报的报文格式
    """

    _name = "cic_taxsb.uniteshenbaosheet"
    _order = "sequence,id"
    _description = '统一申报表模板'
    # _parent_store = True

    parent_id = fields.Many2one('cic_taxsb.uniteshenbaosheet', string='Parent Tag', ondelete='cascade')
    # parent_left = fields.Integer('Parent Left', index=True)
    # parent_right = fields.Integer('Parent Right', index=True)
    child_ids = fields.One2many('cic_taxsb.uniteshenbaosheet', 'parent_id', 'Child Tags')

    name = fields.Char('名称')
    description = fields.Text('说明')  # 说明
    sequence = fields.Integer('序号')  # 排序使用 _order
    tagname = fields.Char('报文标签')
    cells = fields.One2many('cic_taxsb.uniteshenbaosheet.cell', 'sheet_id', string='单元格设置')  # 单元格设置


class UniteShenBaoCell(models.Model):
    """统一申报表单元格定义模板
    模板用来定义最终输出的 申报的报文格式
    """
    _name = "cic_taxsb.uniteshenbaosheet.cell"
    _order = "sequence,id"
    _description = '统一申报表单元格模板'

    sheet_id = fields.Many2one('cic_taxsb.uniteshenbaosheet', '统一申报表', ondelete='cascade')
    sequence = fields.Integer('序号')
    line = fields.Integer('行号', help='统一申报表的行')
    tagname = fields.Char('报文标签')
    get_value_func = fields.Text('取值函数', help='设定本单元格的取数函数代码')
    value = fields.Text(string='单元格的值')
