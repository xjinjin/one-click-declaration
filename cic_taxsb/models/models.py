# -*- coding: utf-8 -*-
# v1
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
    ('00', '[00]公共'),
    ('11', '[11]北京市'),
    ('12', '[12]天津市'),
    ('13', '[13]河北省'),
    ('14', '[14]山西省'),
    ('15', '[15]内蒙古自治区'),
    ('21', '[21]辽宁省'),
    ('22', '[22]吉林省'),
    ('23', '[23]黑龙江省'),
    ('31', '[31]上海市'),
    ('32', '[32]江苏省'),
    ('33', '[33]浙江省'),
    ('34', '[34]安徽省'),
    ('35', '[35]福建省'),
    ('36', '[36]江西省'),
    ('37', '[37]山东省'),
    ('370', '[370]青岛市'),
    ('41', '[41]河南省'),
    ('42', '[42]湖北省'),
    ('43', '[43]湖南省'),
    ('44', '[44]广东省'),
    ('45', '[45]广西壮族自治区'),
    ('46', '[46]海南省'),
    ('50', '[50]重庆市'),
    ('51', '[51]四川省'),
    ('52', '[52]贵州省'),
    ('53', '[53]云南省'),
    ('54', '[54]西藏自治区'),
    ('61', '[61]陕西省'),
    ('62', '[62]甘肃省'),
    ('63', '[63]青海省'),
    ('64', '[64]宁夏回族自治区'),
    ('65', '[65]新疆维吾尔自治区'),
    ('71', '[71]台湾省'),
    ('81', '[81]香港特别行政区'),
    ('82', '[82]澳门特别行政区')
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



# serviceId代码表
SERVICEID_SELECTION = [

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

"""
    xmldict
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Convert xml to python dictionaries.
"""
import datetime


def xml_to_dict(root_or_str, strict=True):
    """
    Converts `root_or_str` which can be parsed xml or a xml string to dict.
    """
    root = root_or_str
    if isinstance(root, str):
        import xml.etree.cElementTree as ElementTree
        root = ElementTree.XML(root_or_str)
    return {root.tag: _from_xml(root, strict)}


def dict_to_xml(dict_xml):
    """
    Converts `dict_xml` which is a python dict to corresponding xml.
    """
    return _to_xml(dict_xml)


# Functions below this line are implementation details.
# Unless you are changing code, don't bother reading.
# The functions above constitute the user interface.

def _to_xml(el):
    """
    Converts `el` to its xml representation.
    """
    val = None
    if isinstance(el, dict):
        val = _dict_to_xml(el)
    elif isinstance(el, bool):
        val = str(el).lower()
    else:
        val = el
    if val is None: val = 'null'
    return val


def _extract_attrs(els):
    """
    Extracts attributes from dictionary `els`. Attributes are keys which start
    with '@'
    """
    if not isinstance(els, dict):
        return ''
    return ''.join(' %s="%s"' % (key[1:], value) for key, value in els.items()
                   if key.startswith('@'))


def _dict_to_xml(els):
    """
    Converts `els` which is a python dict to corresponding xml.
    """

    def process_content(tag, content):
        attrs = _extract_attrs(content)
        text = isinstance(content, dict) and content.get('#text', '') or ''
        return '<%s%s>%s%s</%s>' % (tag, attrs, _to_xml(content), text, tag)

    tags = []
    for tag, content in els.items():
        # Text and attributes
        if tag.startswith('@') or tag == '#text' or tag == '#value':
            continue
        elif isinstance(content, list):
            for el in content:
                tags.append(process_content(tag, el))
        elif isinstance(content, dict):
            tags.append(process_content(tag, content))
        else:
            tags.append('<%s>%s</%s>' % (tag, _to_xml(content), tag))
    return ''.join(tags)


def _str_to_datetime(date_str):
    try:
        val = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        val = date_str
    return val


def _str_to_boolean(bool_str):
    if bool_str.lower() != 'false' and bool(bool_str):
        return True
    return False


def _from_xml(el, strict):
    """
    Extracts value of xml element element `el`.
    """
    val = None
    # Parent node.
    if len(el):
        val = {}
        for e in el:
            tag = e.tag
            v = _from_xml(e, strict)
            if tag in val:
                # Multiple elements share this tag, make them a list
                if not isinstance(val[tag], list):
                    val[tag] = [val[tag]]
                val[tag].append(v)
            else:
                # First element with this tag
                val[tag] = v
    # Simple node.
    else:
        attribs = el.items()
        # An element with attributes.
        if attribs and strict:
            val = dict(('@%s' % k, v) for k, v in dict(attribs).items())
            if el.text:
                converted = _val_and_maybe_convert(el)
                val['#text'] = el.text
                if converted != el.text:
                    val['#value'] = converted
        elif el.text:
            # An element with no subelements but text.
            val = _val_and_maybe_convert(el)
        elif attribs:
            val = dict(attribs)
    return val


def _val_and_maybe_convert(el):
    """
    Converts `el.text` if `el` has attribute `type` with valid value.
    """
    text = el.text.strip()
    data_type = el.get('type')
    convertor = _val_and_maybe_convert.convertors.get(data_type)
    if convertor:
        return convertor(text)
    else:
        return text


_val_and_maybe_convert.convertors = {
    'boolean': _str_to_boolean,
    'datetime': _str_to_datetime,
    'integer': int
}


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
    # sbname = fields.Char('申报名称', default="jbxx", help="基本信息接口 【固定值jbxx】       必须传")
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
    kjzd = fields.Selection(KJZDDM_SELECTION, string='会计制度,必须传', default='1', help="会计制度,必须传")
    nsrzgdm = fields.Selection(NSRZGDM_SELECTION, string='纳税资格代码', help="纳税资格代码 【001增值税一般纳税人/101增值税小规模纳税人】 必须传")
    qyyf = fields.Char('月份-09', help="启用月份(必填) 【系统(当前)月份】          必须传")
    qynf = fields.Char('年份-2019', help="启用年份(必填) 【系统(当前)年份】          必须传")

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


class SBInitJs(models.Model):
    _name = "cic_taxsb.cshjs"
    _description = "江苏初始化前置接口 ，仅限江苏使用"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='02', help="参考代码表  平台申报开放API规范2.0(1)文档")
    sssq = fields.Char('税款所属期', help="税款所属期:('2019-08')")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh',
            'sbzlbh',
            'skssqq',
            'skssqz',
            'nsqxdm',
            'sssq'
        ]
        for record in self:
            # [{'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}]
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)


class SBInit(models.Model):
    _name = "cic_taxsb.csh"
    _description = "初始化往期数据（没有xml 报文） ，江苏地区需要 调用 申报-江苏初始化前置接口，再通过此接口 获取数据"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    # sssq = fields.Char('税款所属期', help="税款所属期:('2019-08')")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='02', help="参考代码表  平台申报开放API规范2.0(1)文档")

    isRenew = fields.Selection(CXHQBZ_SELECTION, string='重新获取标志', default='0', help="重新获取标志")
    serviceId = fields.Char('服务方法标识', default='S002', help="服务方法标识")

    content = fields.Text('报文内容', compute='_compute_content')

    # {'nsrsbh':'91320402MA1Y2G2QX9','sbzlbh':'10101','skssqq':'2019-11-01','skssqz':'2019-11-30','nsqxdm':'02','isRenew':'1'}

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


class SBJk(models.Model):
    _name = "cic_taxsb.jk"
    _description = "申报缴款，支持地区湖南、江苏"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='02', help="参考代码表  平台申报开放API规范2.0(1)文档")
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码(江苏必填)', default='32', help="参考代码表  平台申报开放API规范2.0(1)文档")
    ssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    ssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    sbwj = fields.Char('申报文件(湖南必填)(2019-06-30)', help="申报文件(湖南必填)(2019-06-30)")
    je = fields.Char('金额 必填', help="金额 必填")
    yhzl = fields.Char('银行种类(湖南必填)', help="银行种类(湖南必填)")
    yhdm = fields.Char('银行代码(湖南必填)', help="银行代码(湖南必填)")
    yhzh = fields.Char('银行账号(湖南必填)', help="银行账号(湖南必填)")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh',
            'sbzlbh',
            'nsqxdm',
            'dqbm',
            'ssqq',
            'ssqz',
            'sbwj',
            'je',
            'yhzl',
            'yhdm',
            'yhzh',
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)


class SBQc(models.Model):
    _name = "cic_taxsb.qc"
    _description = "查询当前纳税人能报的税种（没有xml 报文）"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    sssq = fields.Char('税款所属期', help="税款所属期(2019-08)")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh',
            'sbzlbh',
            'skssqq',
            'skssqz',
            'sssq'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)


class SBZf(models.Model):
    _name = "cic_taxsb.zf"
    _description = "作废已申报税种（没有xml 报文）"
    _inherit = "cic_taxsb.base"

    lsh = fields.Char('申报提交得流水号 必传', help="申报提交得流水号 必传")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    skssq = fields.Char('税款所属期', help="税款所属期:('2019-06')")
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', default='32', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='02', help="参考代码表  平台申报开放API规范2.0(1)文档")
    # {'lsh':'','nsrsbh':'','sbzlbh':'','skssqq':'','skssqz':'','skssq':'','dqbm':'','nsqxdm':''}
    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'lsh',
            'nsrsbh',
            'sbzlbh',
            'skssqq',
            'skssqz',
            'skssq',
            'dqbm',
            'nsqxdm'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)


class SBSfxy(models.Model):
    _name = "cic_taxsb.sfxy"
    _description = "三方协议，支持湖南、贵州地区"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)


class SBStatus(models.Model):
    _name = "cic_taxsb.status"
    _description = "申报结果查询接口"
    _inherit = "cic_taxsb.base"

    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号 必须传")
    # sbname = fields.Char('查询申报状态 固定这个值', default="sbzt", help="查询申报状态 固定这个值")
    # kjnd = fields.Char('年份', help="年份(2019)")
    # kjqj = fields.Char('月份', help="月份(01)  申报得税款所属期止 的 月份")
    # lsh = fields.Char('申报提交得流水号 必传', help="申报提交得流水号 必传")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', help="参考代码表")
    skssqq = fields.Char('税款所属期起,格式yyyy-MM-dd', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止,格式yyyy-MM-dd', help="税款所属期止:('2019-08-31')")

    serviceId = fields.Char('服务方法标识', default='S004', help="服务方法标识")
    # {'sbzlbh':'','nsrsbh':'','sbname':'','kjnd':'','kjqj':'','lsh':''}
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


class SBSubmit(models.Model):
    _name = "cic_taxsb.submit"
    _description = "提交申报数据,税种不同，报文不同"

    # 和xml报文一起组成字典content,这几个字段是提交必填项。单独出来
    lsh = fields.Char(string='申报提交得流水号 必传', help="申报提交得流水号 必传")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='02', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssq = fields.Char('税款所属期止 年-月份（2019-05）', help='税款所属期止 年-月份（2019-05）')
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='29806', help="参考代码表  平台申报开放API规范2.0(1)文档")
    serviceId = fields.Char(compute='_compute_serviceId', string='申报种类编号(自动生成)',
                            help='申报种类编号加Submit就是serviceId，例如：10101Submit')

    @api.multi
    def create_lsh(self):
        for record in self:
            record.lsh = uuid.uuid4()

    @api.depends('sbzlbh')
    def _compute_serviceId(self):
        self.serviceId = self.sbzlbh + 'Submit'


# 江苏报文,xml
class ShenBaoSheet(models.Model):
    """申报表模板
    模板用来定义最终输出的 申报的报文格式,
    分地区报表类型，利用定义每个单元格的模式来实现对任何种类表格的取数和生成报文需要
    """

    _name = "cic_taxsb.shenbaosheet"
    _order = "sequence,id"
    _description = '申报表模板'
    # _parent_store = True

    parent_id = fields.Many2one('cic_taxsb.shenbaosheet', string='Parent Tag', ondelete='cascade')
    # parent_left = fields.Integer('Parent Left', index=True)
    # parent_right = fields.Integer('Parent Right', index=True)
    child_ids = fields.One2many('cic_taxsb.shenbaosheet', 'parent_id', 'Child Tags')

    name = fields.Char('名称')
    description = fields.Text('说明')  # 说明
    structure = fields.Char('表的结构编码')
    sequence = fields.Integer('序号')  # 排序使用 _order
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', required=True, help='地区编码')  # 分地区
    tagname = fields.Char('报文标签')
    cells = fields.One2many('cic_taxsb.shenbaosheet.cell', 'sheet_id', string='单元格设置')  # 单元格设置
    template = fields.Text('模板', help='备用的模板信息')


class ShenBaoCell(models.Model):
    """申报表单元格定义模板
    模板用来定义最终输出的 申报的报文格式,
     单元格所在行号，名称，取数接口
    """
    _name = "cic_taxsb.shenbaosheet.cell"
    _order = "sequence,id"
    _description = '申报表单元格模板'

    sheet_id = fields.Many2one('cic_taxsb.shenbaosheet', '申报表', ondelete='cascade')  #
    sequence = fields.Integer('序号')  # 排序
    line = fields.Integer('行号', help='申报表的行')  # 行号，一行两个行次
    line_num = fields.Char('行次', help='此处行次并不是出报表的实际的行数,只是显示用的用来符合国人习惯')  # 行次
    tagname = fields.Char('报文标签')  #
    get_value_func = fields.Text('取值函数', help='设定本单元格的取数函数代码')
    key = fields.Char('取值的key')  # 测试用
    # value = fields.Float(string = '取得的值',digits=(10,2))
    value = fields.Text(string='取得的值')
    temp_dict = fields.Text('temp_dict')  # 没用


class CreateShenbaoSheetWizard(models.TransientModel):
    """创建申报报文的向导"""
    _name = "create.shenbaosheet.wizard"
    _description = '申报表的向导'
    _inherit = ['cic_taxsb.submit', 'cic_taxsb.base']

    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', required=True, help='地区编码')
    sheet_id = fields.Many2one('cic_taxsb.shenbaosheet', '申报表', required=True)  # 39
    account_id = fields.Many2one('cic_ocr_report.account', '账套', required=True, help='对应总账系统的账套信息')  # 100
    startdate = fields.Date('开始日期', required=True, help='开始日期')  # 2019-09-01
    enddate = fields.Date('截止日期', required=True, help='截止日期')  # 2019-09-30

    xml = fields.Text('XML报文')
    content = fields.Text('报文内容', compute='_compute_content')

    # {'dqbm': '32', 'sheet_id': 108,'account_id': 100, 'startdate': '2019-09-01', 'enddate': '2019-09-30'}
    # {'nsrsbh': '91320214MA1NYKMBXK', 'nsqxdm': '1','skssqz': '2019-07-01', 'sbzlbh': '29806'}
    # {'appkey': '3ccb2aab00e149eab2b9567fbf508217', 'token': '515d582419d2ee937d2f8084'}
    @api.multi
    def create_shenbao_sheet(self):
        """
        申报表的创建函数
        ShenBaoSheet：创建xml，parent_id和child_ids表示3个对象之间的关系，cells代表所有的单元格
        ShenBaoCell：创建单元格。sheet_id表示属于那个表
        CreateShenbaoSheetWizard：创建xml。sheet_id表示属于那个xml
        """
        for record in self:  # xml
            res = record.env['cic_tools.cic_finance'].get_declaration_data(record.account_id.levyNum, record.startdate,
                                                                           record.enddate)
            # res = record.env['cic_tools.cic_finance'].get_declaration_data('91320214MA1NYKMBXK','2019-07-01','2019-09-30')
            two_temp_dict = {}
            one_temp_dict = {record.sheet_id.tagname: two_temp_dict}

            '''
            组织成标准的字典模式：one_temp_dict = {'jsxgs_cwbb_xqykjzzxxVO': {'jsxgs_cwbb_xqykjzz_zcfzb': {'zcfzbGridlbVO': [{'a':'a'},{'a':'a'}..]}, 'sbbinfo': {'a':'a'}, 'jsxgs_cwbb_xqykjzz_xjllb': null, 'jsxgs_cwbb_xqykjzz_lrb': {'lrbGridlbVO': [{'a':'a'},{'a':'a'}..]}}}
            1. {'form_name': null}
            2. {'form_name': {'':'',..}}         
            3. {form_name:{'line_name':[{'ewbhxh':'1',...},...]}}
            4. {form_name:{'line_name':[{'ewbhxh':'1','floatrow':'1',...},...]}}
            5. {form_name:{'line_name':{'ewbhxh':'1','floatrow':'1',...}}}
            6. {form_name:{'line_name':{'ewbhxh':'1',...}}}
            7. {form_name:{'item_name':{'cell_name':'cell_value',...},'item_name':{'cell_name':'cell_value',...},..}}
            8. {form_name:{'items_name':{'item_name':{'cell_name':'cell_value',...},'item_name':{'cell_name':'cell_value',...},..}}}
            此8种情况分别讨论，组成一个字典（one_temp_dict）即可。
            xml_name,form_name,line_name,cell_name      (form--cell)
            xml_name,form_name,[items_name],item_name,cell_name       (form--item_name--cell)
            '''
            for forms in record.sheet_id.child_ids:  # xml的表对象

                # 8. {form_name:{'items_name':{'item_name':{'cell_name':'cell_value',...},'item_name':{'cell_name':'cell_value',...},..}}}
                if forms.structure == '8':
                    items_dict = {}
                    for item in forms.child_ids.child_ids:
                        item_dict = {}
                        for cell in item.cells:
                            key = cell.tagname
                            # exec(cell.get_value_func,{'res':res,'cell':cell})
                            # value = cell.value
                            value = '110'
                            item_dict[key] = value
                        items_dict[item.tagname] = item_dict
                    two_temp_dict[forms.tagname] = {forms.child_ids.tagname: items_dict}

                # 7. {form_name:{'item_name':{'cell_name':'cell_value',...},'item_name':{'cell_name':'cell_value',...},..}}
                elif forms.structure == '7':
                    form_dict = {}
                    for item in forms.child_ids:
                        item_dict = {}
                        for cell in item.cells:
                            key = cell.tagname
                            # exec(cell.get_value_func,{'res':res,'cell':cell})
                            # value = cell.value
                            value = '110'
                            item_dict[key] = value
                        form_dict[item.tagname] = item_dict
                    two_temp_dict[forms.tagname] = form_dict

                # 6. {form_name:{'line_name':{'ewbhxh':'1',...}}}
                elif forms.structure == '6':
                    line_dict = {'ewbhxh': '1'}
                    form_dict = {forms.child_ids.tagname: line_dict}
                    for cell in forms.cells:
                        key = cell.tagname
                        # exec(cell.get_value_func,{'res':res,'cell':cell})
                        # value = cell.value
                        value = '110'
                        line_dict[key] = value
                    two_temp_dict[forms.tagname] = form_dict

                # 5. {form_name:{'line_name':{'ewbhxh':'1','floatrow':'1',...}}}
                elif forms.structure == '5':
                    line_dict = {'ewbhxh': '1', 'floatrow': '1'}
                    form_dict = {forms.child_ids.tagname: line_dict}
                    for cell in forms.cells:
                        key = cell.tagname
                        # exec(cell.get_value_func,{'res':res,'cell':cell})
                        # value = cell.value
                        value = '110'
                        line_dict[key] = value
                    two_temp_dict[forms.tagname] = form_dict

                # 4. {form_name:{'line_name':[{'ewbhxh':'1','floatrow':'1',...},...]}}
                elif forms.structure == '4':
                    big_cells_dict = {}
                    for cell in forms.cells:
                        key = cell.tagname
                        # exec(cell.get_value_func,{'res':res,'cell':cell})
                        # value = cell.value
                        value = '110'
                        if str(cell.line) not in big_cells_dict:
                            big_cells_dict[str(cell.line)] = {'ewbhxh': cell.line, 'floatrow': '1'}
                            big_cells_dict[str(cell.line)][key] = value
                        else:
                            big_cells_dict[str(cell.line)][key] = value
                    #  [{'a': 'a', 'b': 'b'}, {'a': 'a', 'b': 'b'}, {'a': 'a', 'b': 'b'}]
                    # {"lrbGridlbVO": [{"jyycbbyje": "","jyycbbnljje": "","ewbhxh": "2"},{}]}
                    # {'jsxgs_cwbb_xqykjzz_lrb':{"lrbGridlbVO": [{},{}]}}
                    two_temp_dict[forms.tagname] = {forms.child_ids.tagname: list(big_cells_dict.values())}

                # 3. {form_name:{'line_name':[{'ewbhxh':'1',...},...]}}
                elif forms.structure == '3':
                    big_cells_dict = {}
                    for cell in forms.cells:
                        key = cell.tagname
                        # exec(cell.get_value_func,{'res':res,'cell':cell})
                        # value = cell.value
                        value = '110'
                        if str(cell.line) not in big_cells_dict:
                            big_cells_dict[str(cell.line)] = {'ewbhxh': cell.line}
                            big_cells_dict[str(cell.line)][key] = value
                        else:
                            big_cells_dict[str(cell.line)][key] = value
                    #  [{'a': 'a', 'b': 'b'}, {'a': 'a', 'b': 'b'}, {'a': 'a', 'b': 'b'}]
                    # {"lrbGridlbVO": [{"jyycbbyje": "","jyycbbnljje": "","ewbhxh": "2"},{}]}
                    # {'jsxgs_cwbb_xqykjzz_lrb':{"lrbGridlbVO": [{},{}]}}
                    two_temp_dict[forms.tagname] = {forms.child_ids.tagname: list(big_cells_dict.values())}

                # 2. {'form_name': {'':'',..}}
                elif forms.structure == '2':  # 申报信息.表没有行对象
                    form_cell_dict = {}  # {"nsqxdm": "1","ssqq": "2019-01-01"}
                    for cell in forms.cells:
                        key = cell.tagname
                        # exec(cell.get_value_func,{'record':record,'cell':cell})
                        # value = cell.value
                        value = '110'
                        form_cell_dict[key] = value
                    two_temp_dict[forms.tagname] = form_cell_dict  # {'sbbinfo':{"nsqxdm": "1","ssqq": "2019-01-01"}}

                # 1. {'form_name': null}
                else:  # 现金流量表
                    two_temp_dict[forms.tagname] = ''
            record.xml = dict_to_xml(one_temp_dict)

    @api.multi
    def _compute_content(self):
        _fields = [
            'lsh',
            'serviceId',
            'nsrsbh',
            'nsqxdm',
            'skssq'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]  # {'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}
            # temp_dict = record.read(_fields)  # [{'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}]
            temp_dict.pop('id', None)  # {'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}
            xmlStr = '<?xml version="1.0" encoding="UTF-8"?>{}'.format(record.xml)
            temp_dict['bizXml'] = base64.b64encode(xmlStr.encode('utf-8')).decode("utf-8")
            record.content = json.dumps(temp_dict)


class CreateXmlObjWizard(models.TransientModel):
    """上传xml文件，xml所需对象"""
    _name = "create.xml.obj.wizard"
    _description = '创建xml的向导'

    name = fields.Char(string='申报提交xml报文', required=True, help='增值税一般纳税人申报表接口(月报).xml')
    description = fields.Text(string='说明', default='财务报表涉及到行次问题，不能使用此功能', readonly=True)
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', required=True, help='地区编码')
    file = fields.Binary(string="Upload Xml File")

    @api.one
    def create_xml_obj(self):
        xml = str(base64.b64decode(self.file), encoding='utf-8')
        file_name_no_extend, extension_name = os.path.splitext(self.name)

        shenbaosheetcell = self.env['cic_taxsb.shenbaosheet.cell']  # 单元格
        shenbaosheet = self.env['cic_taxsb.shenbaosheet']  # 表

        xml_dict = xml_to_dict(xml)

        # xml 创建xml
        xml_name = list(xml_dict.keys())[0]  # jsxgs_zzs_ybnsrxxVO
        xml_obj = shenbaosheet.create(
            {'name': file_name_no_extend, 'description': file_name_no_extend, 'dqbm': self.dqbm, 'tagname': xml_name})
        xml_id = xml_obj.id

        '''
            1. {'form_name': null}
            2. {'form_name': {'':'',..}}
            3. {form_name:{'line_name':[{'ewbhxh':'1',...},...]}}
            4. {form_name:{'line_name':[{'ewbhxh':'1','floatrow':'1',...},...]}}
            5. {form_name:{'line_name':{'ewbhxh':'1','floatrow':'1',...}}}
            6. {form_name:{'line_name':{'ewbhxh':'1',...}}}
            7. {form_name:{'item_name':{'cell_name':'cell_value',...},'item_name':{'cell_name':'cell_value',...},..}}
            8. {form_name:{'items_name':{'item_name':{'cell_name':'cell_value',...},'item_name':{'cell_name':'cell_value',...},..}}}'''
        # {'jsxgs_zzs_ybnsrxxVO':{'sbbinfo':{'sbzlbh':'10101',...},'jsxgs_zzs_ybnsr_sbb':{'sbbGridlbVO':[{'ewbhxh':'1',...},...]},'jsxgs_zzs_ybnsr_scqy15':None,...}}
        # print(list(xml_dict.keys())[0]) #   xml_dict.keys():dict_keys(['jsxgs_zzs_ybnsrxxVO'])

        forms_name = list(list(xml_dict.values())[0].keys())  # ['sbbinfo', 'jsxgs_zzs_ybnsr_sbb',...]
        for form_name in forms_name:
            # 2-8
            if isinstance(xml_dict[xml_name][form_name], dict):
                # 5,6,7,8
                if isinstance(list(xml_dict[xml_name][form_name].values())[0], dict):
                    # 8. {form_name:{'items_name':{'item_name':{'cell_name':'cell_value',...},'item_name':{'cell_name':'cell_value',...},..}}}
                    if isinstance(list(list(xml_dict[xml_name][form_name].values())[0].values())[0], dict):
                        # 创建表
                        form_obj = shenbaosheet.create(
                            {'parent_id': xml_id, 'name': form_name, 'description': form_name, 'dqbm': self.dqbm,
                             'tagname': form_name, 'structure': '8'})
                        form_id = form_obj.id
                        # 创建items
                        items_name = list(xml_dict[xml_name][form_name].keys())[0]
                        items_obj = shenbaosheet.create(
                            {'parent_id': form_id, 'name': items_name, 'description': items_name, 'dqbm': self.dqbm,
                             'tagname': items_name})
                        items_id = items_obj.id
                        # 创建item
                        item_name_list = list(xml_dict[xml_name][form_name][items_name].keys())
                        for item_name in item_name_list:
                            item_obj = shenbaosheet.create(
                                {'parent_id': items_id, 'name': item_name, 'description': item_name, 'dqbm': self.dqbm,
                                 'tagname': item_name})
                            item_id = item_obj.id
                            # 创建单元格     与item关联    无行号
                            cell_name_list = list(xml_dict[xml_name][form_name][items_name][item_name].keys())
                            for cell_name in cell_name_list:
                                shenbaosheetcell.create({'sheet_id': item_id, 'tagname': cell_name})

                    # 7. {form_name:{'item_name':{'cell_name':'cell_value',...},'item_name':{'cell_name':'cell_value',...},..}}
                    elif len(list(xml_dict[xml_name][form_name].keys())) > 1:
                        # 创建表
                        form_obj = shenbaosheet.create(
                            {'parent_id': xml_id, 'name': form_name, 'description': form_name, 'dqbm': self.dqbm,
                             'tagname': form_name, 'structure': '7'})
                        form_id = form_obj.id
                        # 创建item
                        item_name_list = list(xml_dict[xml_name][form_name].keys())
                        for item_name in item_name_list:
                            item_obj = shenbaosheet.create(
                                {'parent_id': form_id, 'name': item_name, 'description': item_name, 'dqbm': self.dqbm,
                                 'tagname': item_name})
                            item_id = item_obj.id
                            # 创建单元格     与item关联    无行号
                            cell_name_list = list(xml_dict[xml_name][form_name][item_name].keys())
                            for cell_name in cell_name_list:
                                shenbaosheetcell.create(
                                    {'sheet_id': item_id, 'tagname': cell_name})

                    # 6. {form_name:{'line_name':{'ewbhxh':'1',...}}}
                    elif 'floatrow' not in list(xml_dict[xml_name][form_name].values())[0]:
                        # 创建表
                        form_obj = shenbaosheet.create(
                            {'parent_id': xml_id, 'name': form_name, 'description': form_name, 'dqbm': self.dqbm,
                             'tagname': form_name, 'structure': '6'})
                        form_id = form_obj.id
                        # 创建行
                        line_name = list(xml_dict[xml_name][form_name].keys())[0]
                        shenbaosheet.create(
                            {'parent_id': form_id, 'name': line_name, 'description': line_name, 'dqbm': self.dqbm,
                             'tagname': line_name})
                        # 创建单元格     与表关联    无行号
                        cell_name_list = list(xml_dict[xml_name][form_name][line_name].keys())
                        for cell_name in cell_name_list:
                            if cell_name != 'ewbhxh':
                                shenbaosheetcell.create(
                                    {'sheet_id': form_id, 'tagname': cell_name})

                    # 5. {form_name:{'line_name':{'ewbhxh':'1','floatrow':'1',...}}}
                    elif 'floatrow' in list(xml_dict[xml_name][form_name].values())[0]:
                        # 创建表
                        form_obj = shenbaosheet.create(
                            {'parent_id': xml_id, 'name': form_name, 'description': form_name, 'dqbm': self.dqbm,
                             'tagname': form_name, 'structure': '5'})
                        form_id = form_obj.id
                        # 创建行
                        line_name = list(xml_dict[xml_name][form_name].keys())[0]
                        shenbaosheet.create(
                            {'parent_id': form_id, 'name': line_name, 'description': line_name, 'dqbm': self.dqbm,
                             'tagname': line_name})
                        # 创建单元格     与表关联    无行号
                        cell_name_list = list(xml_dict[xml_name][form_name][line_name].keys())
                        for cell_name in cell_name_list:
                            if cell_name not in ['ewbhxh', 'floatrow']:
                                shenbaosheetcell.create(
                                    {'sheet_id': form_id, 'tagname': cell_name})
                    else:
                        pass

                # 3,4
                elif isinstance(list(xml_dict[xml_name][form_name].values())[0], list):
                    # 4. {form_name:{'line_name':[{'ewbhxh':'1','floatrow':'1',...},...]}}
                    # 2层字典里一个v,v是列表，v里的字典里有'floatrow'
                    if len(list(xml_dict[xml_name][form_name].values())) == 1 \
                            and isinstance(list(xml_dict[xml_name][form_name].values())[0], list) \
                            and 'floatrow' in list(xml_dict[xml_name][form_name].values())[0][0]:
                        # 创建表
                        form_obj = shenbaosheet.create(
                            {'parent_id': xml_id, 'name': form_name, 'description': form_name, 'dqbm': self.dqbm,
                             'tagname': form_name, 'structure': '4'})
                        form_id = form_obj.id
                        # 创建行
                        line_name = list(xml_dict[xml_name][form_name].keys())[0]
                        shenbaosheet.create(
                            {'parent_id': form_id, 'name': line_name, 'description': line_name, 'dqbm': self.dqbm,
                             'tagname': line_name})
                        # 创建单元格     与表关联    有行号
                        for cell_dict in xml_dict[xml_name][form_name][line_name]:
                            cell_line_num = int(cell_dict['ewbhxh'])
                            cell_name_list = list(cell_dict.keys())
                            for cell_name in cell_name_list:
                                if cell_name not in ['ewbhxh', 'floatrow']:
                                    shenbaosheetcell.create(
                                        {'sheet_id': form_id, 'line': cell_line_num, 'tagname': cell_name})

                    # 3. {form_name:{'line_name':[{'ewbhxh':'1',...},...]}}
                    # 2层字典里一个v,v是列表，v里的字典里没有'floatrow'
                    if len(list(xml_dict[xml_name][form_name].values())) == 1 \
                            and isinstance(list(xml_dict[xml_name][form_name].values())[0], list) \
                            and 'floatrow' not in list(xml_dict[xml_name][form_name].values())[0][0]:
                        # 创建表
                        form_obj = shenbaosheet.create(
                            {'parent_id': xml_id, 'name': form_name, 'description': form_name, 'dqbm': self.dqbm,
                             'tagname': form_name, 'structure': '3'})
                        form_id = form_obj.id
                        # 创建行
                        line_name = list(xml_dict[xml_name][form_name].keys())[0]
                        shenbaosheet.create(
                            {'parent_id': form_id, 'name': line_name, 'description': line_name, 'dqbm': self.dqbm,
                             'tagname': line_name})
                        # 创建单元格     与表关联    有行号
                        for cell_dict in xml_dict[xml_name][form_name][line_name]:
                            cell_line_num = int(cell_dict['ewbhxh'])
                            cell_name_list = list(cell_dict.keys())
                            for cell_name in cell_name_list:
                                if cell_name != 'ewbhxh':
                                    shenbaosheetcell.create(
                                        {'sheet_id': form_id, 'line': cell_line_num, 'tagname': cell_name})

                # 2
                else:  # 2. {'form_name': {'':'',..}}
                    # 创建表
                    form_obj = shenbaosheet.create(
                        {'parent_id': xml_id, 'name': form_name, 'description': form_name, 'dqbm': self.dqbm,
                         'tagname': form_name, 'structure': '2'})
                    form_id = form_obj.id
                    # 创建单元格     与表关联    无行号
                    cell_name_list = list(xml_dict[xml_name][form_name].keys())
                    for cell_name in cell_name_list:
                        shenbaosheetcell.create({'sheet_id': form_id, 'tagname': cell_name})

            # 1.
            else:  # {'form_name': null}
                # 创建表
                shenbaosheet.create(
                    {'parent_id': xml_id, 'name': form_name, 'description': form_name, 'dqbm': self.dqbm,
                     'tagname': form_name, 'structure': '1'})


# 统一报文，json

comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

cell_stable_value = ['lmc', 'ewblxh', 'ewbhxh', 'hmc', 'xmmc', 'lc', 'jmxzdmjmc', 'msxmdmjmc', 'zsxmMc', 'zspmMc',
                     'zsxmDm', 'zspmDm', 'xm']


class UniteCreateShenbaoSheetWizard(models.TransientModel):
    """根据统一报文对象，创建统一报文格式"""
    _name = "create.uniteshenbaosheet.wizard"
    _description = '申报表的向导'
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
    def create_uniteshenbao_sheet(self):
        '''根据统一报文对象，创建统一报文格式. dict/json ?'''
        for record in self:
            # res = record.env['cic_tools.cic_finance'].get_declaration_data(record.account_id.levyNum, record.startdate,record.enddate)
            # res = record.env['cic_tools.cic_finance'].get_declaration_data('91320214MA1NYKMBXK','2019-07-01','2019-09-30')

            level_one_dict = {}
            for level_one_obj in record.sheet_id.cells:
                level_one_dict[level_one_obj.tagname] = level_one_obj.value
            for level_one_obj in record.sheet_id.child_ids:
                if level_one_obj.tagname == 'head':
                    level_two_dict = {}
                    for cell in level_one_obj.cells:
                        key = cell.tagname
                        value = 0
                        level_two_dict[key] = value
                    level_one_dict[level_one_obj.tagname] = level_two_dict
                if level_one_obj.tagname == 'note':
                    level_two_dict = {}
                    for cell in level_one_obj.cells:
                        key = cell.tagname
                        value = cell.value
                        level_two_dict[key] = value
                    level_one_dict[level_one_obj.tagname] = level_two_dict
                if level_one_obj.tagname == 'body':
                    level_two_dict = {}
                    for level_two_obj in level_one_obj.child_ids:
                        level_three_dict = {} # 构建3层字典。     1.dict      2.list

                        for level_three_obj in level_two_obj.child_ids:
                            level_four_dict = {}
                            for cell in level_three_obj.cells:
                                key = cell.tagname
                                value = 0
                                if cell.line:
                                    if str(cell.line) not in level_four_dict:
                                        level_four_dict[str(cell.line)] = {}
                                        level_four_dict[str(cell.line)][key] = value
                                    else:
                                        level_four_dict[str(cell.line)][key] = value
                                else:
                                    level_four_dict[key] = value
                            if isinstance(list(level_four_dict.values())[0], dict):
                                level_three_dict[level_three_obj.tagname] = list(level_four_dict.values())
                            else:
                                level_three_dict[level_three_obj.tagname] = level_four_dict

                        level_two_dict[level_two_obj.tagname] = level_three_dict
                    level_one_dict[level_one_obj.tagname] = level_two_dict
            record.create_dict = level_one_dict

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
            if record.create_dict:
                temp_dict = record.read(_fields)[0]  # {'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}
                # temp_dict = record.read(_fields)  # [{'id': 2,'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}]
                temp_dict.pop('id', None)  # {'gsdlfs': '2', 'gsnsmm': 'Jj111111', 'qyyf': '09'}
                content = json.dumps(record.create_dict)
                temp_dict['bizXml'] = base64.b64encode(content.encode('utf-8')).decode("utf-8")
                record.content = json.dumps(temp_dict)

class UniteCreateJsonObjWizard(models.TransientModel):
    """上传统一报文json文件，创建统一报文对象（自动增加项暂未考虑）"""
    _name = "unite.create.json.obj.wizard"
    _description = '创建json的向导'

    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', help="地区编码")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', help="参考代码表")
    name = fields.Char(string='json报文名称', help='比如：附加税交付报文_V20191015.json')
    file = fields.Binary(string="Upload")

    @api.one
    def create_json_obj(self):
        # bytes--->str
        content_str = base64.b64decode(self.file).decode('utf-8')

        content_dict = eval(content_str)

        file_name_no_extend, extension_name = os.path.splitext(self.name)
        shenbaosheetcell = self.env['cic_taxsb.uniteshenbaosheet.cell']
        shenbaosheet = self.env['cic_taxsb.uniteshenbaosheet']

        level_one_keys = list(content_dict.keys())

        # 创建抽象0层的对象
        level_zero_key_obj = shenbaosheet.create({'name': file_name_no_extend, 'tagname': 'level_zero_key'})
        level_zero_key_id = level_zero_key_obj.id

        # 创建第一层.    version head body note
        for level_one_key in level_one_keys:
            if level_one_key == 'version':
                shenbaosheetcell.create({'sheet_id': level_zero_key_id, 'tagname': level_one_key, 'value': 'default'})
            if level_one_key == 'head':
                level_one_key_obj = shenbaosheet.create({'parent_id': level_zero_key_id, 'tagname': level_one_key})
                level_one_key_id = level_one_key_obj.id
                # 创建第二层.
                level_two_dict = content_dict[level_one_key]
                level_two_keys = list(level_two_dict.keys())
                for level_two_key in level_two_keys:
                    shenbaosheetcell.create({'sheet_id': level_one_key_id, 'tagname': level_two_key})
            if level_one_key == 'note':
                level_one_key_obj = shenbaosheet.create({'parent_id': level_zero_key_id, 'tagname': level_one_key})
                level_one_key_id = level_one_key_obj.id
                # 创建第二层.
                level_two_dict = content_dict[level_one_key]
                level_two_keys = list(level_two_dict.keys())
                for level_two_key in level_two_keys:
                    shenbaosheetcell.create({'sheet_id': level_one_key_id, 'tagname': level_two_key,'value': level_two_dict[level_two_key]})
            if level_one_key == 'body':
                level_one_key_obj = shenbaosheet.create({'parent_id': level_zero_key_id, 'tagname': level_one_key})
                level_one_key_id = level_one_key_obj.id
                # 创建第二层.
                level_two_dict = content_dict[level_one_key]
                level_two_keys = list(level_two_dict.keys())
                for level_two_key in level_two_keys:
                    level_two_key_obj = shenbaosheet.create({'parent_id': level_one_key_id, 'tagname': level_two_key})
                    level_two_key_id = level_two_key_obj.id

                    # 创建第三层
                    level_three_dict = level_two_dict[level_two_key]
                    level_three_keys = list(level_three_dict.keys())
                    for level_three_key in level_three_keys:
                        level_three_key_obj = shenbaosheet.create({'parent_id': level_two_key_id, 'tagname': level_three_key})
                        level_three_key_id = level_three_key_obj.id

                        # 创建第四层      1.dict      2.list
                        level_four = level_three_dict[level_three_key]
                        if isinstance(level_four, dict):
                            level_four_keys = list(level_four.keys())
                            for level_four_key in level_four_keys:
                                shenbaosheetcell.create({'sheet_id': level_three_key_id, 'tagname': level_four_key})
                        if isinstance(level_four, list):
                            line = 0
                            for level_five_dict in level_four:
                                line = line + 1
                                level_five_keys = list(level_five_dict.keys())
                                for level_five_key in level_five_keys:
                                    shenbaosheetcell.create({'sheet_id': level_three_key_id, 'tagname': level_five_key,'line':line})


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
