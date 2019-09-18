# -*- coding: utf-8 -*-

from odoo import models, fields, api
from hashlib import sha256
import hmac
import base64
import uuid
import requests
import json

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
        val = datetime.datetime.strptime(date_str,  "%Y-%m-%dT%H:%M:%SZ")
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

    host = fields.Char('主机',default='211.151.124.80')
    port = fields.Integer('端口',default=6006)
    path = fields.Char('接口地址',default='remote/callServer')
    appkey = fields.Char('appKey',default="68c8c236c8484b35b149019d590ff0b0")
    token = fields.Char('token',default="7f182e426e1a5508c40bbdfa")
    content = fields.Text('jsonData',default='{}')

    @api.one
    def post(self, content=None):
        url = "http://{}:{}/{}".format(self.host,self.port,self.path)
        content = content or self.content
        params = {
            "appKey": self.appkey,
            "token": hmac.new(bytes(self.token,'utf-8'),msg=bytes(content,'utf-8'),digestmod=sha256).hexdigest(),
            "jsonData": content
        }
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        res = requests.post(url,data=params,headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            return res.text

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

NSRZGDM_SELECTION = [
    ('001', '增值税一般纳税人'),
    ('101', '增值税小规模纳税人'),
]

DLFS_SELECTION = [
    ('1','CA登录'),
    ('2','密码登录'),
    ('3','实名账号'),
]

SZDM_SELECTION = [
    ('10101','增值税一般纳税人申报表'),
    ('10102','增值税小规模申报表'),
    ('10516','城建税、教育费附加、地方教育附加税(费)申报表(月)'),
    ('B0516','城建税、教育费附加、地方教育附加税(费)申报表(季)'),
    ('10502','城镇土地使用税纳税申报表'),
    ('10520','地方各项基金费申报表（月报）'),
    ('B0520','地方各项基金费申报表（季）'),
    ('10501','房产税纳税申报表'),
    ('90201','综合所得申报表'),
    ('10512','分类所得申报表'),
    ('10513','非居民所得申报表'),
    ('10524','个人经营所得A类'),
    ('10412','企业所得税月（季）报A类'),
    ('10413','企业所得税月（季）报B类'),
    ('90106','社会保险费缴纳表'),
    ('10601','文化事业建设费(新国税)'),
    ('39805','财务报表(企业会计制度)'),
    ('29806','财务报表(小企业会计准则)'),
    ('10311','消费税（电池）申报表'),
    ('10111','印花税纳税申报表(新)月/季'),
    ('B0111','印花税纳税申报表(选报)次'),
    ('B9805','财务报表(企业会计准则)'),
    ('C0502','财务报表(企业会计准则)'),
    ('90601','生产经营所得纳税申报表'),
    ('10306','消费税其他'),
    ('42016','增值税预缴申报'),
    ('10521','土地增值税纳税申报表'),
    ('10517','残疾人就业保障金缴费申报表 月'),
    ('B0517','残疾人就业保障金缴费申报表 季'),
]

NSQXDM_SELECTION = [
    ('1','月'),
    ('2','季'),
    ('3','半年'),
    ('4','年'),
    ('5','次'),
]

class SBDjxx(models.Model):
    _name = "cic_taxsb.djxx"
    _description = "登记税号基本信息"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号 必须传")
    qymc = fields.Char('企业名称', help="企业名称 必须传")
    sbname = fields.Char('申报名称', default="jbxx", help="基本信息接口 【固定值jbxx】       必须传")
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', help="地区编码【参考地区编码 平台申报开放API规范2.0(1)文档】 必须传")
    cwlxr = fields.Char('财务联系人', help="财务联系人          【江苏必须传】")
    cwlxrlxfs = fields.Char('财务联系人联系电话', help="财务联系人联系电话  【江苏必须传】")
    dscsdlmm = fields.Char('地税CA密码', help="地税CA密码 目前不支持")
    dsdlfs = fields.Selection(DLFS_SELECTION, string='地税登录方式', default='2', help="地税登录方式 1 CA(目前不支持线上，需要联系运维人员) 2 用户名密码")
    dsdlmm = fields.Char('地税登录密码', help="地税登录密码")
    dsdlyhm = fields.Char('地税登录名', help="地税登录名")
    gscamm = fields.Char('国税CA密码', help="国税CA密码【(目前不支持线上，需要联系运维人员) 】")
    gsdlfs = fields.Selection(DLFS_SELECTION, string='国税登录方式', default='2', help="国税登录方式 【1: CA(目前不支持线上，需要联系运维人员) 2: 用户名密码(税号)  3:实名账号(江苏无需此类型) 】")
    gsnsmm = fields.Char('国税登录密码', help="国税登录密码                      必须传")
    gsnsrsbh = fields.Char('国税纳税人识别号', help="纳税人识别号        必须传")
    gsnsyhm = fields.Char('国税登录名', help="国税登录名            必须传")
    kjzd = fields.Char('kjzd', default='1', help="必须传")
    nsrzgdm = fields.Selection(NSRZGDM_SELECTION, string='nsrzgdm', help="纳税资格代码 【001增值税一般纳税人/101增值税小规模纳税人】 必须传")
    qyyf = fields.Char('月份', help="启用月份(必填) 【系统(当前)月份】          必须传")
    qynf = fields.Char('年份', help="启用年份(必填) 【系统(当前)年份】          必须传")

    content = fields.Text('报文内容', compute='_compute_content')


    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh',
            'qymc',
            'sbname',
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
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id',None)
            res_dict = {'jsds_jbxxVO':{'sbbinfo':temp_dict}}
            xmlStr = '<?xml version="1.0" encoding="UTF-8"?>{}'.format(dict_to_xml(res_dict))
            record.content = json.dumps({'bizXml':base64.b64encode(xmlStr.encode('utf-8')).decode("utf-8")})

class SBInitJs(models.Model):
    _name = "cic_taxsb.cshjs"
    _description = "江苏初始化前置接口 ，仅限江苏使用"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码',default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码',default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")
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
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)

class SBInit(models.Model):
    _name = "cic_taxsb.csh"
    _description = "初始化往期数据（没有xml 报文） ，江苏地区需要 调用 申报-江苏初始化前置接口，再通过此接口 获取数据"
    _inherit = "cic_taxsb.base"

    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码',default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    sssq = fields.Char('税款所属期', help="税款所属期:('2019-08')")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码',default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'nsrsbh',
            'sbzlbh',
            'skssqq',
            'skssqz',
            'sssq',
            'nsqxdm'
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
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码',default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")
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
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码',default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
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
    _description = "查询最终申报结果"
    _inherit = "cic_taxsb.base"

    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号 必须传")
    sbname = fields.Char('查询申报状态 固定这个值', default="sbzt", help="查询申报状态 固定这个值")
    kjnd = fields.Char('年份', help="年份(2019)")
    kjqj = fields.Char('月份', help="月份(01)  申报得税款所属期止 的 月份")
    lsh = fields.Char('申报提交得流水号 必传', help="申报提交得流水号 必传")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'sbzlbh',
            'nsrsbh',
            'sbname',
            'kjnd',
            'kjqj'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id',None)
            res_dict = {'jsds_sbztxxVO':{'sbbinfo':temp_dict}}
            xmlStr = '<?xml version="1.0" encoding="UTF-8"?>{}'.format(dict_to_xml(res_dict))
            record.content = json.dumps({'bizXml':base64.b64encode(xmlStr.encode('utf-8')).decode("utf-8"),
                                         'lsh':record.lsh})

# class SBSubmit(models.Model):
#     _name = "cic_taxsb.submit"
#     _description = "提交申报数据"
#     _inherit = "cic_taxsb.base"
#
#     sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
#     nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号 必须传")
#     sbname = fields.Char('查询申报状态 固定这个值', default="sbzt", help="查询申报状态 固定这个值")
#     kjnd = fields.Char('年份', help="年份(2019)")
#     kjqj = fields.Char('月份', help="月份(01)  申报得税款所属期止 的 月份")
#     lsh = fields.Char('申报提交得流水号 必传', help="申报提交得流水号 必传")
#
#     content = fields.Text('报文内容', compute='_compute_content')
#
#     @api.multi
#     def _compute_content(self):
#         _fields = [
#             'sbzlbh',
#             'nsrsbh',
#             'sbname',
#             'kjnd',
#             'kjqj'
#         ]
#         for record in self:
#             temp_dict = record.read(_fields)[0]
#             temp_dict.pop('id',None)
#             res_dict = {'jsds_sbztxxVO':{'sbbinfo':temp_dict}}
#             xmlStr = '<?xml version="1.0" encoding="UTF-8"?>{}'.format(dict_to_xml(res_dict))
#             record.content = json.dumps({'bizXml':base64.b64encode(xmlStr.encode('utf-8')).decode("utf-8"),
#                                          'lsh':record.lsh})

class SBZf(models.Model):
    _name = "cic_taxsb.zf"
    _description = "作废"
    _inherit = "cic_taxsb.base"

    lsh = fields.Char('申报提交得流水号 必传', help="申报提交得流水号 必传")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码',default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    skssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    sssq = fields.Char('税款所属期', help="税款所属期(2019-08)")
    dqbm = fields.Selection(DQBM_SELECTION, string='地区编码', default='32', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        _fields = [
            'lsh',
            'nsrsbh',
            'sbzlbh',
            'skssqq',
            'skssqz',
            'sssq',
            'dqbm',
            'nsqxdm'
        ]
        for record in self:
            temp_dict = record.read(_fields)[0]
            temp_dict.pop('id', None)
            record.content = json.dumps(temp_dict)