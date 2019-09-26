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
    ('1','CA登录'),
    ('2','密码登录'),
    ('3','实名账号'),
]

# 税种代码表
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

# serviceId代码表
SERVICEID_SELECTION = [
    ('10101Submit','增值税一般纳税人申报表'),
    ('10102Submit','增值税小规模申报表'),
    ('10516Submit','城建税、教育费附加、地方教育附加税(费)申报表(月)'),
    ('B0516Submit','城建税、教育费附加、地方教育附加税(费)申报表(季)'),
    ('10502Submit','城镇土地使用税纳税申报表'),
    ('10520Submit','地方各项基金费申报表（月报）'),
    ('B0520Submit','地方各项基金费申报表（季）'),
    ('10409Submit','地税企业所得税A类（查账，2018年版）'),
    ('10410Submit','地税企业所得税B类（核定，2018年版）'),
    ('10501Submit','房产税纳税申报表'),
    ('10511Submit','综合所得申报表'),
    ('10512Submit','分类所得申报表'),
    ('10513Submit','非居民所得申报表'),
    ('10524Submit','个人经营所得A类'),
    ('10412Submit','企业所得税月（季）报A类'),
    ('10413Submit','企业所得税月（季）报B类'),
    ('90106Submit','社会保险费缴纳表'),
    ('10601Submit','文化事业建设费(新国税)'),
    ('39805Submit','财务报表(企业会计制度)'),
    ('29806Submit','财务报表(小企业会计准则)'),
    ('10311Submit','消费税（电池）申报表'),
    ('10111Submit','印花税纳税申报表(新)'),
    ('B0111Submit','印花税纳税申报表(选报)'),
    ('B9805Submit','财务报表(企业会计准则)'),
    ('C0502Submit','地方各项基金费申报表（选报）基金申报表')
]

# 纳税期限代码
NSQXDM_SELECTION = [
    ('1','月'),
    ('2','季'),
    ('3','半年'),
    ('4','年'),
    ('5','次'),
]

# 配偶标志
POBZ_SELECTION = [
    ('0','无'),
    ('1','有')
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

class SBSubmit(models.Model):
    _name = "cic_taxsb.submit"
    _description = "提交申报数据,税种不同，报文不同"

    # 和xml报文一起组成字典content,这几个字段是提交必填项。单独出来
    lsh = fields.Char('申报提交得流水号 必传', help="申报提交得流水号 必传")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")
    skssqz = fields.Char('税款所属期止', help='税款所属期止')
    serviceId = fields.Char(compute='_compute_serviceId',string = '申报种类编号(自动生成)',
                            help='申报种类编号加Submit就是serviceId，例如：10101Submit')
    @api.onchange('sbzlbh')
    def _compute_serviceId(self):
        self.serviceId = self.sbzlbh + 'Submit'

class SBXqykjzz(models.Model):
    _name = "cic_taxsb.xqykjzz"
    _description = "财务报表(小企业会计准则)月(季)"
    _inherit = ['cic_taxsb.base', 'cic_taxsb.submit']

    # 每个税种表都有这几个字段，单独出来。xml。此对象提交
    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    ssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    ssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    area = fields.Selection(DQBM_SELECTION, string='地区编码', default='32', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")

    # all the records.  self.post().  inverse_name字段等于当前记录.     不存储
    xqykjzz_line = fields.One2many('cic_taxsb.xqykjzz.line', 'xqykjzz_id')

class SBXqykjzzline(models.Model):
    _name = "cic_taxsb.xqykjzz.line"
    _description = "财务报表(小企业会计准则)月(季)"

    # 0/1 record.   存储
    xqykjzz_id = fields.Many2one('cic_taxsb.xqykjzz')

    # 短期借款
    ewbhxh = fields.Char('行次', help="行次")
    dqjkqmye = fields.Char('期末余额', help="期末余额")
    hbzjncye = fields.Char('年初余额', help="年初余额")
    hbzjqmye = fields.Char('期末余额', help="期末余额")
    dqjkncye = fields.Char('年初余额', help="年初余额")

    # 应付票据
    # ewbhxh = fields.Char('行次', help="行次")
    yfpjqmye = fields.Char('期末余额', help="期末余额")
    dqtzqmye = fields.Char('期末余额', help="期末余额")
    yfpjncye = fields.Char('年初余额', help="年初余额")
    dqtzncye = fields.Char('年初余额', help="年初余额")

    # 应收票据
    # ewbhxh = fields.Char('行次', help="行次")
    yspjqmye = fields.Char('期末余额', help="期末余额")
    yfzkncye = fields.Char('年初余额', help="年初余额")
    yfzkqmye = fields.Char('期末余额', help="期末余额")
    yspjncye = fields.Char('年初余额', help="年初余额")

    # 预收帐款
    # ewbhxh = fields.Char('行次', help="行次")
    ygszkqmye = fields.Char('应收账款##期末余额', help="应收账款##期末余额")
    yszkqmye = fields.Char('预收帐款##期末余额', help="预收帐款##期末余额")
    ygszkncye = fields.Char('应收账款##年初余额', help="应收账款##年初余额")
    yszkncye = fields.Char('预收帐款##年初余额', help="预收帐款##年初余额")

    # 预付账款
    # ewbhxh = fields.Char('行次', help="行次")
    yfzkqmye = fields.Char('期末余额', help="期末余额")
    yfzkncye = fields.Char('年初余额', help="年初余额")
    yfzgxcncye = fields.Char('年初余额', help="年初余额")
    yfzgxcqmye = fields.Char('期末余额', help="期末余额")

    # 应收股利
    # ewbhxh = fields.Char('行次', help="行次")
    ysglqmye = fields.Char('期末余额', help="期末余额")
    yjsfqmye = fields.Char('期末余额', help="期末余额")
    yjsfncye = fields.Char('年初余额', help="年初余额")
    ysglncye = fields.Char('年初余额', help="年初余额")

    # 应付利息
    # ewbhxh = fields.Char('行次', help="行次")
    yflxncye = fields.Char('年初余额', help="年初余额")
    yslxqmye = fields.Char('期末余额', help="期末余额")
    yslxncye = fields.Char('年初余额', help="年初余额")
    yflxqmye = fields.Char('期末余额', help="期末余额")

    # 应付利润
    # ewbhxh = fields.Char('行次', help="行次")
    yflrncye = fields.Char('年初余额', help="年初余额")
    qtyskncye = fields.Char('年初余额', help="年初余额")
    qtyskqmye = fields.Char('期末余额', help="期末余额")
    yflrqmye = fields.Char('期末余额', help="期末余额")

    # 存货
    # ewbhxh = fields.Char('行次', help="行次")
    chqmye = fields.Char('期末余额', help="期末余额")
    qtyfkncye = fields.Char('年初余额', help="年初余额")
    chncye = fields.Char('年初余额', help="年初余额")
    qtyfkqmye = fields.Char('期末余额', help="期末余额")

    # 其他流动负债
    # ewbhxh = fields.Char('行次', help="行次")
    qtldfzqmye = fields.Char('期末余额', help="期末余额")
    qzyclncye = fields.Char('年初余额', help="年初余额")
    qzyclqmye = fields.Char('期末余额', help="期末余额")
    qtldfzncye = fields.Char('年初余额', help="年初余额")

    # 在产品
    # ewbhxh = fields.Char('行次', help="行次")
    zcpncye = fields.Char('年初余额', help="年初余额")
    ldfzhjqmye = fields.Char('期末余额', help="期末余额")
    zcpqmye = fields.Char('期末余额', help="期末余额")
    ldfzhjncye = fields.Char('年初余额', help="年初余额")

    # 库存材料
    # ewbhxh = fields.Char('行次', help="行次")
    kcclncye = fields.Char('年初余额', help="年初余额")
    kcclqmye = fields.Char('期末余额', help="期末余额")

    # 周转材料
    # ewbhxh = fields.Char('行次', help="行次")
    zzclqmye = fields.Char('期末余额', help="期末余额")
    zqjkqmye = fields.Char('期末余额', help="期末余额")
    zzclncye = fields.Char('年初余额', help="年初余额")
    zqjkncye = fields.Char('年初余额', help="年初余额")

    # 长期应付款
    # ewbhxh = fields.Char('行次', help="行次")
    zqyfkncye = fields.Char('年初余额', help="年初余额")
    qtldzcqmye = fields.Char('期末余额', help="期末余额")
    qtldzcncye = fields.Char('年初余额', help="年初余额")
    zqyfkqmye = fields.Char('期末余额', help="期末余额")

    # 递延收益
    # ewbhxh = fields.Char('行次', help="行次")
    dysyqmye = fields.Char('期末余额', help="期末余额")
    ldzchjqmye = fields.Char('期末余额', help="期末余额")
    ldzchjncye = fields.Char('年初余额', help="年初余额")
    dysyncye = fields.Char('年初余额', help="年初余额")



class SBGrjysdsxx(models.Model):
    _name = "cic_taxsb.grjysdsxx"
    _description = "个人经营所得A类"
    _inherit = ['cic_taxsb.base', 'cic_taxsb.submit']

    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    ssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    ssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    area = fields.Selection(DQBM_SELECTION, string='地区编码', default='32', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")

    # 个人经营所得A类 个人所得税生产经营所得纳税申报表(a表)
    ewbhxh = fields.Char(default='1')
    # ewbhxh = fields.Char(default='2')
    floatrow = fields.Char(default='1')
    ynssde = fields.Char('应纳税所得额',help='应纳税所得额')
    zsfs = fields.Char('征收方式',help='征收方式')
    qylx = fields.Char('企业类型',help='企业类型')
    skssqz = fields.Char('税款所属期止',help='税款所属期止')
    # nsrsbh = fields.Char('纳税人识别号',help='纳税人识别号')
    btzdwnsrsbh = fields.Char('被投资单位纳税人识别号',help='被投资单位纳税人识别号')
    mbyqndks = fields.Char('弥补以前年度亏损',help='弥补以前年度亏损')
    cbfy = fields.Char('成本费用',help='成本费用')
    sfzjhm = fields.Char('身份证件号码',help='身份证件号码')
    lrze = fields.Char('利润总额',help='利润总额')
    jmse = fields.Char('减免税额',help='减免税额')
    gjdq = fields.Char('国籍(地区)',help='国籍(地区)')
    ybtse = fields.Char('应补(退)税额',help='应补(退)税额')
    yyjse = fields.Char('已预缴税额',help='已预缴税额')
    ynse = fields.Char('应纳税额',help='应纳税额')
    srze = fields.Char('收入总额',help='收入总额')
    skssqq = fields.Char('税款所属期起',help='税款所属期起')
    hhqyhhrfpbl = fields.Char('合伙企业合伙人分配比例(%)',help='合伙企业合伙人分配比例(%)')
    btzdwmc = fields.Char('被投资单位名称',help='被投资单位名称')
    sskcs = fields.Char('速算扣除数',help='速算扣除数')
    sfzjlx = fields.Char('身份证件类型',help='身份证件类型')
    tzzjcfy = fields.Char('投资者减除费用',help='投资者减除费用')
    xm = fields.Char('姓名',help='姓名')
    yssdl = fields.Char('应税所得率(%)',help='应税所得率(%)')
    sl = fields.Char('税率(%)',help='税率(%)')

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        pass

    # ewbhxh = fields.Char('2',default = '2',help='2')
    # floatrow = fields.Char('1',default = '1',help='1')
    # btzdwnsrsbh = fields.Char('被投资单位纳税人识别号',help='被投资单位纳税人识别号')
    # yyjse = fields.Char('已预缴税额',help='已预缴税额')
    # lrze = fields.Char('利润总额',help='利润总额')
    # skssqz = fields.Char('税款所属期止',help='税款所属期止')
    # nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    # zsfs = fields.Char('征收方式',help='征收方式')
    # cbfy = fields.Char('成本费用',help='成本费用')
    # hhqyhhrfpbl = fields.Char('合伙企业合伙人分配比例(%)',help='合伙企业合伙人分配比例(%)')
    # tzzjcfy = fields.Char('投资者减除费用',help='投资者减除费用')
    # yssdl = fields.Char('应税所得率(%)',help='应税所得率(%)')
    # ynse = fields.Char('应纳税额',help='应纳税额')
    # qylx = fields.Char('企业类型',help='企业类型')
    # xm = fields.Char('姓名',help='姓名')
    # btzdwmc = fields.Char('被投资单位名称',help='被投资单位名称')
    # srze = fields.Char('收入总额',help='收入总额')
    # sskcs = fields.Char('速算扣除数',help='速算扣除数')
    # sfzjhm = fields.Char('身份证件号码',help='身份证件号码')
    # mbyqndks = fields.Char('弥补以前年度亏损',help='弥补以前年度亏损')
    # sfzjlx = fields.Char('身份证件类型',help='身份证件类型')
    # sl = fields.Char('税率(%)',help='税率(%)')
    # jmse = fields.Char('减免税额', help='减免税额')
    # gjdq = fields.Char('国籍(地区)',help='国籍(地区)')
    # ybtse = fields.Char('应补(退)税额',help='应补(退)税额')
    # skssqq = fields.Char('税款所属期起',help='税款所属期起')
    # ynssde = fields.Char('应纳税所得额',help='应纳税所得额')
    #

    #
    # @api.multi
    # def _compute_content(self):
    #     _fields0 = [
    #         'sbzlbh',
    #         'ssqq',
    #         'ssqz',
    #         'nsrsbh',
    #         'area'
    #     ]
    #     _fields1 = [
    #         'ynssde',
    #         'zsfs',
    #         'qylx',
    #         'skssqz',
    #         'nsrsbh',
    #         'btzdwnsrsbh',
    #         'mbyqndks',
    #         'cbfy',
    #         'sfzjhm',
    #         'lrze',
    #         'jmse',
    #         'gjdq',
    #         'ybtse',
    #         'yyjse',
    #         'ynse',
    #         'srze',
    #         'skssqq',
    #         'hhqyhhrfpbl',
    #         'btzdwmc',
    #         'sskcs',
    #         'sfzjlx',
    #         'tzzjcfy',
    #         'xm',
    #         'yssdl',
    #         'sl',
    #     ]
    #     _fields2 = [
    #         'ewbhxh',
    #         'floatrow',
    #         'btzdwnsrsbh',
    #         'yyjse',
    #         'lrze',
    #         'skssqz',
    #         'nsrsbh',
    #         'zsfs',
    #         'cbfy',
    #         'hhqyhhrfpbl',
    #         'tzzjcfy',
    #         'yssdl',
    #         'ynse',
    #         'qylx',
    #         'xm',
    #         'btzdwmc',
    #         'srze',
    #         'sskcs',
    #         'sfzjhm',
    #         'mbyqndks',
    #         'sfzjlx',
    #         'sl',
    #         'jmse',
    #         'gjdq',
    #         'ybtse',
    #         'skssqq',
    #         'ynssde'
    #     ]
    #     for record in self:
    #         temp_dict0 = record.read(_fields0)[0]
    #         temp_dict0.pop('id',None)
    #         temp_dict1 = record.read(_fields1)[0]
    #         temp_dict1.pop('id',None)
    #         temp_dict2 = record.read(_fields2)[0]
    #         temp_dict2.pop('id',None)
    #         res_dict = {'jsds_sbztxxVO':{'sbbinfo':temp_dict0,
    #                                      'jsds_grjysds_zb':{'zbGridlbVO':temp_dict1,'zbGridlbVO':temp_dict2},
    #                                      'jsds_grjysds_jmssx':'',
    #                                      'jsds_grjysds_jcxxb_b':''}}
    #         xmlStr = '<?xml version="1.0" encoding="UTF-8"?>{}'.format(dict_to_xml(res_dict))
    #         record.content = json.dumps({'lsh':record.lsh,
    #                                      'bizXml':base64.b64encode(xmlStr.encode('utf-8')).decode("utf-8"),
    #                                      'nsrsbh':record.nsrsbh,
    #                                      'nsqxdm':record.nsqxdm,
    #                                      'skssq':record.skssq,
    #                                      'serviceId':record.sbzlbh+'Submit'
    #                                      })

class SBFlsdsbxx(models.Model):
    _name = "cic_taxsb.flsdsbxx"
    _description = "分类所得申报表"
    _inherit = ['cic_taxsb.base', 'cic_taxsb.submit']

    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    ssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    ssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    area = fields.Selection(DQBM_SELECTION, string='地区编码', default='32', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")

    ewbhxh = fields.Char(default='1')
    floatrow = fields.Char(default='1')
    bz = fields.Char('备注', help='备注')
    jzdzxxdz = fields.Char('居住地址(详细地址)', help='居住地址(详细地址)')
    sfcj = fields.Boolean('是否残疾',default = False, help='True/False')
    sfls = fields.Boolean('是否烈属', default = False, help='True/False')
    zzlx = fields.Char('证照类型', help='证照类型')
    jzdzqx = fields.Char('居住地址(区县)',help='居住地址(区县)')
    rzsgrq = fields.Char('任职受雇日期', help='任职受雇日期')
    hjszdqx = fields.Char('户籍所在地(区县)', help='户籍所在地(区县)')
    sfjwry = fields.Boolean('是否境外人员', default = False, help='True/False')
    hjszdsh = fields.Char('户籍所在地(省)', help='户籍所在地(省)')
    jzdzs = fields.Char('居住地址(市)', help='居住地址(市)')
    lxdzxxdz = fields.Char('联系地址(详细地址)', help='联系地址(详细地址)')
    gh = fields.Char('工号', help='工号')
    ryzt = fields.Char('人员状态', help='人员状态')
    lszh = fields.Char('烈属证号', help='烈属证号')
    lxdzqx = fields.Char('联系地址(区县)', help='联系地址(区县)')
    csrq = fields.Char('出生日期', help='出生日期')
    cjzh = fields.Char('残疾证号', help='残疾证号')
    lxdzs = fields.Char('联系地址(市)', help='联系地址(市)')
    lzrq = fields.Char('离职日期', help='离职日期')
    hjszdxxdz = fields.Char('户籍所在地(详细地址)', help='户籍所在地(详细地址)')
    xl = fields.Char('学历', help='学历')
    sfgy = fields.Boolean('是否雇员',default = True, help='True/False')
    yjljsj = fields.Char('预计离境时间', help='预计离境时间')
    csgjdq = fields.Char('出生国家(地区)', help='出生国家(地区)')
    zwm = fields.Char('中文名', help='中文名')
    hjszds = fields.Char('户籍所在地(市)', help='户籍所在地(市)')
    grtzbl = fields.Char('个人投资比例(%)', help='个人投资比例(%)')
    sfgl = fields.Boolean('是否孤老', default = False, help='True/False')
    zw = fields.Char('职务', help='职务')
    qtzzlx = fields.Char('其他证照类型', help='其他证照类型')
    xb = fields.Char('性别', help='性别')
    qtzzhm = fields.Char('其他证照号码', help='其他证照号码')
    khyx = fields.Char('开户银行', help='开户银行')
    xm = fields.Char('姓名', help='姓名')
    grtze = fields.Char('个人投资额', help='个人投资额')
    zzhm = fields.Char('证照号码', help='证照号码')
    scrjsj = fields.Char('首次入境时间', help='首次入境时间')
    jzdzsh = fields.Char('居住地址(省)', help='居住地址(省)')
    yxzh = fields.Char('银行账号', help='银行账号')
    dzyx = fields.Char('电子邮箱', help='电子邮箱')
    lxdzsh = fields.Char('联系地址(省)', help='联系地址(省)')
    sjhm = fields.Char('手机号码', help='手机号码')
    gjdq = fields.Char('国籍(地区)', help='国籍(地区)')

    mssr = fields.Char('免税收入', help='免税收入')
    jzfs = fields.Char('捐赠方式', help='捐赠方式')
    # bz = fields.Char('备注', help='备注')
    # zzhm = fields.Char('证照号码', help='证照号码')
    # yzf = fields.Char()
    # zzlx = fields.Char('证照类型', help='证照类型')
    jmse = fields.Char('减免税额', help='减免税额')
    sdxm = fields.Char('所得项目', help='所得项目')
    sjjze = fields.Char('实际捐赠额', help='实际捐赠额')
    sr = fields.Char('收入', help='收入')
    jajsbl = fields.Char('减按计税比例', help='减按计税比例')
    zykcdjze = fields.Char('准予扣除的捐赠额', help='准予扣除的捐赠额')

    nscount = fields.Char(default = '7')
    nsamount = fields.Char(default = '36010.00')
    gsgbze = fields.Char(default = '0')
    totalYbtse = fields.Char(default = '0')

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        pass

class SBZhsbsdxx(models.Model):
    _name = "cic_taxsb.zhsbsdxxV"
    _description = "个税综合所得申报表"
    _inherit = ['cic_taxsb.base', 'cic_taxsb.submit']

    sbzlbh = fields.Selection(SZDM_SELECTION, string='申报种类编码', default='10101', help="参考代码表  平台申报开放API规范2.0(1)文档")
    ssqq = fields.Char('税款所属期起', help="税款所属期起:('2019-08-01')")
    ssqz = fields.Char('税款所属期止', help="税款所属期止:('2019-08-31')")
    nsrsbh = fields.Char('申报的纳税人识别号', help="申报的纳税人识别号")
    area = fields.Selection(DQBM_SELECTION, string='地区编码', default='32', help="参考代码表  平台申报开放API规范2.0(1)文档")
    nsqxdm = fields.Selection(NSQXDM_SELECTION, string='纳税期限代码', default='1', help="参考代码表  平台申报开放API规范2.0(1)文档")

    ewbhxh = fields.Char(default='1')
    floatrow = fields.Char(default='1')
    bz = fields.Char('备注', help='备注')
    jzdzxxdz = fields.Char('居住地址(详细地址)', help='居住地址(详细地址)')
    sfcj = fields.Boolean('是否残疾', default=False, help='True/False')
    sfls = fields.Boolean('是否烈属', default=False, help='True/False')
    zzlx = fields.Char('证照类型', help='证照类型')
    jzdzqx = fields.Char('居住地址(区县)', help='居住地址(区县)')
    rzsgrq = fields.Char('任职受雇日期', help='任职受雇日期')
    hjszdqx = fields.Char('户籍所在地(区县)', help='户籍所在地(区县)')
    sfjwry = fields.Boolean('是否境外人员', default=False, help='True/False')
    hjszdsh = fields.Char('户籍所在地(省)', help='户籍所在地(省)')
    jzdzs = fields.Char('居住地址(市)', help='居住地址(市)')
    lxdzxxdz = fields.Char('联系地址(详细地址)', help='联系地址(详细地址)')
    gh = fields.Char('工号', help='工号')
    ryzt = fields.Char('人员状态', help='人员状态')
    lszh = fields.Char('烈属证号', help='烈属证号')
    lxdzqx = fields.Char('联系地址(区县)', help='联系地址(区县)')
    csrq = fields.Char('出生日期', help='出生日期')
    cjzh = fields.Char('残疾证号', help='残疾证号')
    lxdzs = fields.Char('联系地址(市)', help='联系地址(市)')
    rzsgcyrq = fields.Char('任职受雇从业日期', help='任职受雇从业日期')
    lzrq = fields.Char('离职日期', help='离职日期')
    hjszdxxdz = fields.Char('户籍所在地(详细地址)', help='户籍所在地(详细地址)')
    xl = fields.Char('学历', help='学历')
    yjljsj = fields.Char('预计离境时间', help='预计离境时间')
    csgjdq = fields.Char('出生国家(地区)', help='出生国家(地区)')
    zwm = fields.Char('中文名', help='中文名')
    hjszds = fields.Char('户籍所在地(市)', help='户籍所在地(市)')
    grtzbl = fields.Char('个人投资比例(%)', help='个人投资比例(%)')
    sfgl = fields.Boolean('是否孤老', default=False, help='True/False')
    zw = fields.Char('职务', help='职务')
    qtzzlx = fields.Char('其他证照类型', help='其他证照类型')
    xb = fields.Char('性别', help='性别')
    qtzzhm = fields.Char('其他证照号码', help='其他证照号码')
    khyx = fields.Char('开户银行', help='开户银行')
    xm = fields.Char('姓名', help='姓名')
    grtze = fields.Char('个人投资额', help='个人投资额')
    zzhm = fields.Char('证照号码', help='证照号码')
    scrjsj = fields.Char('首次入境时间', help='首次入境时间')
    jzdzsh = fields.Char('居住地址(省)', help='居住地址(省)')
    dzyx = fields.Char('电子邮箱', help='电子邮箱')
    lxdzsh = fields.Char('联系地址(省)', help='联系地址(省)')
    sjhm = fields.Char('手机号码', help='手机号码')
    gjdq = fields.Char('国籍(地区)', help='国籍(地区)')

    gh = fields.Char('工号', help='工号')
    jbylbxf = fields.Char('基本养老保险费', help='基本养老保险费')
    syylbx = fields.Char('税延养老保险', help='税延养老保险')
    ljzfdklx = fields.Char('累计住房贷款利息', help='累计住房贷款利息')
    xm = fields.Char('姓名', help='姓名')
    bqsr = fields.Char('本期免税收入', help='本期免税收入')
    zzhm = fields.Char('证照号码', help='证照号码')
    bz = fields.Char('备注', help='备注')
    zzlx = fields.Char('证照类型', help='证照类型')
    qt = fields.Char('其他', help='其他')
    ljzfzj = fields.Char('累计住房租金', help='累计住房租金')
    jmse = fields.Char('减免税额', help='减免税额')
    sybxf = fields.Char('失业保险费', help='失业保险费')
    ljjxjy = fields.Char('累计继续教育', help='累计继续教育')
    syjkbx = fields.Char('商业健康保险', help='商业健康保险')
    zykcdjze = fields.Char('准予扣除的捐赠额', help='准予扣除的捐赠额')
    zfgjj = fields.Char('住房公积金', help='住房公积金')
    qyzynj = fields.Char('企业(职业)年金', help='企业(职业)年金')
    ljznjy = fields.Char('累计子女教育', help='累计子女教育')
    ljsylr = fields.Char('累计赡养老人', help='累计赡养老人')
    jbyilbxf = fields.Char('基本医疗保险费', help='基本医疗保险费')

    ewbhxh = fields.Char(default='1')
    floatrow = fields.Char(default='1')
    syjkbx = fields.Char('商业健康保险', help='商业健康保险')
    qt = fields.Char('其他', help='其他')
    bz = fields.Boolean('备注', help='备注')
    zzlx = fields.Char('证照类型', help='证照类型')
    syylbx = fields.Char('税延养老保险', help='税延养老保险')
    jmse = fields.Char('减免税额', help='减免税额')
    bqmssr = fields.Char('本期免税收入', help='本期免税收入')
    gh = fields.Boolean('工号', help='工号')
    bqsr = fields.Char('本期收入', help='本期收入')
    zzhm = fields.Char('证照号码', help='证照号码')
    sdxm = fields.Char('所得项目', help='所得项目')
    zykcdjze = fields.Char('准予扣除的捐赠额', help='准予扣除的捐赠额')
    xm = fields.Char('姓名', help='姓名')

    ewbhxh = fields.Char(default = '1')
    floatrow = fields.Char(default = '1')
    syylbx = fields.Char('税延养老保险', help='税延养老保险')
    zzhm = fields.Char('证照号码', help='证照号码')
    gh = fields.Char('工号', help='工号')
    syjkbx = fields.Char('商业健康保险', help='商业健康保险')
    rzsgcyrq = fields.Char('任职受雇从业日期', help='任职受雇从业日期')
    qyzynj = fields.Char('企业(职业)年金', help='企业(职业)年金')
    qt = fields.Char('其他', help='其他')
    xm = fields.Char('姓名', help='姓名')
    jmse = fields.Char('减免税额', help='减免税额')
    mssr = fields.Char('免税收入', help='免税收入')
    ykjse = fields.Char('已扣缴税额', help='已扣缴税额')
    bz = fields.Char('备注', help='备注')
    qnycxjje = fields.Char('全年一次性奖金额', help='全年一次性奖金额')
    zzlx = fields.Boolean('证照类型',help='证照类型')
    zykcdjze = fields.Char('准予扣除的捐赠额', help='准予扣除的捐赠额')

    '''
    综合所得申报表	减免事项附表
    综合所得申报表	商业健康保险附表
    综合所得申报表	税延养老保险附表
    专项人员信息
    '''

    kKjnd = fields.Char(default = '0')
    kRyxm = fields.Char()
    kZjlx = fields.Char('证件类型', help='证件类型')
    khyx = fields.Char('开户银行', help='开户银行')
    xm = fields.Char('姓名', help='姓名')
    grtze = fields.Char('个人投资额', help='个人投资额')
    zzhm = fields.Char('证照号码', help='证照号码')
    kPobz = fields.Selection(POBZ_SELECTION,string = '配偶标志', help='配偶标志')
    kPoxm = fields.Char('配偶姓名', help='配偶姓名')
    kPozjlx = fields.Char('配偶证件类型', help='配偶证件类型')
    kDsznbz = fields.Selection(DSZNBZ_SELECTION,string = '独生子女标志', help='独生子女标志')
    kSylrftfs = fields.Char('赡养老人分摊方式', help='赡养老人分摊方式')
    kSylrbndykcje = fields.Integer('养老人本年度月扣除金额', help='养老人本年度月扣除金额')

    # 子女信息
    kZnxm = fields.Char('子女姓名',help='子女姓名')
    kZjlx = fields.Char('证件类型',help='证件类型')
    kZjhm = fields.Char('证件号码',help='证件号码')
    kCsrq = fields.Char('出生日期',help='出生日期')
    kGj = fields.Char('国籍',help='国籍')
    kDqsjyjd = fields.Char('当前受教育阶段',help='当前受教育阶段')
    kDqsjyjdqssj = fields.Char('当前受教育阶段起始时间',help='当前受教育阶段起始时间')
    kDqsjyjdjssj = fields.Char('当前受教育阶段结束时间',help='当前受教育阶段结束时间')
    kJyzzsj = fields.Char('教育终止时间',help='教育终止时间')
    kDqjdqj = fields.Char('当前就读国籍',help='当前就读国籍')
    kDqjdxx = fields.Char('当前就读学校',help='当前就读学校')
    kBrkcbl = fields.Char('本人扣除比例',help='本人扣除比例')

    # 住房租金
    kProvince = fields.Char('主要工作省份', help='主要工作省份')
    kCity = fields.Char('主要工作城市', help='主要工作城市')
    kCzflx = fields.Char('出租方类型', help='出租方类型')
    kCzfxm = fields.Char('出租方姓名（组织名称）', help='出租方姓名（组织名称）')
    kCzfzjlx = fields.Char('出租方证件类型', help='出租方证件类型')
    kCzfzjhm = fields.Char('出租方证件号码（统一社会信用代码）', help='出租方证件号码（统一社会信用代码）')
    kZfzldz = fields.Char('住房坐落地址', help='住房坐落地址')
    kZfzlhtbh = fields.Char('租赁合同编号', help='租赁合同编号')
    kZlqq = fields.Char('租赁期起', help='租赁期起')
    kZlqz = fields.Char('租赁期止', help='租赁期止')

    # 住房贷款 住房信息
    kFwzldz = fields.Char('房屋坐落地址', help='房屋坐落地址')
    kBrjkbz = fields.Selection(BRJKBZ_SELECTION,string = '本人借款标志 0-否 1-是', help='本人借款标志 0-否 1-是')
    kZfzslx = fields.Char('住房证书类型', help='住房证书类型')
    kZfzsh = fields.Char('住房证书号', help='住房证书号')
    kDklx = fields.Selection(DKLX_SELECTION,string = '贷款类型 1-公积金贷款 2-商业贷款', help='贷款类型 1-公积金贷款 2-商业贷款')
    kDkyh = fields.Char('贷款银行', help='贷款银行')
    kDkhtbh = fields.Char('贷款合同编号', help='贷款合同编号')
    kSchkrq = fields.Char('首次还款日期', help='首次还款日期')
    kDkqx = fields.Char('贷款期限(月数)', help='贷款期限(月数)')

    # 赡养老人 被赡养人信息
    kXm1 = fields.Char('姓名', help='姓名')
    kZjlx1 = fields.Char('证件类型', help='证件类型')
    kZjhm1 = fields.Char('证件号码', help='证件号码')
    kGj1 = fields.Char('国籍', help='国籍')
    kGx1 = fields.Char('关系', help='关系')
    kCsrq1 = fields.Char('出生日期', help='出生日期')

    # 共同赡养人信息
    kXm2 = fields.Char('姓名', help='姓名')
    kZjlx2 = fields.Char('证件类型', help='证件类型')
    kZjhm2 = fields.Char('证件号码', help='证件号码')
    kGj2 = fields.Char('国籍', help='国籍')

    # 继续教育
    kJyjd = fields.Char('教育阶段', help='教育阶段')
    kRxsj = fields.Char('入学时间', help='入学时间')
    kBysj = fields.Char('毕业时间', help='毕业时间')
    kJxjylx = fields.Char('继续教育类型', help='继续教育类型')
    kFzrq = fields.Char('发证（批准）日期', help='发证（批准）日期')
    kZsmc = fields.Char('证书名称', help='证书名称')
    kZsbh = fields.Char('证书编号', help='证书编号')
    kFzjg = fields.Char('发证机关', help='发证机关')

    nscount = fields.Char('纳税人数', help='纳税人数')
    nsamount = fields.Char('纳税金额', help='纳税金额')
    gsgbze = fields.Char('公司股本总额', help='公司股本总额')
    totalYbtse = fields.Char('应补退税额', help='应补退税额')

    content = fields.Text('报文内容', compute='_compute_content')

    @api.multi
    def _compute_content(self):
        pass

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