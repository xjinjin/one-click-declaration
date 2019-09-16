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



    
    

