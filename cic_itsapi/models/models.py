# -*- coding: utf-8 -*-

from odoo import models, fields, api
from hashlib import sha256
import base64
import uuid
import requests
import json
from Crypto.Cipher import AES
from urllib.parse import quote_plus
import time
import re

pkcs5padding = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def encrypt(content, encodeRules):
    encode = AES.new(str.encode(encodeRules), AES.MODE_ECB)
    return base64.encodebytes(encode.encrypt(pkcs5padding(content))).decode()

def decrypt(content, encodeRules):
    decode = AES.new(str.encode(encodeRules), AES.MODE_ECB)
    data =  decode.decrypt(base64.b64decode(content)).decode()
    result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', data)
    return result



class itsAPIMixin(models.Model):
    _name = "cic_itsapi.base"
    _description = 'itsAPI base'

    api_url = fields.Char('url',default='https://itsapi.holytax.com/v5/api/s')
    appid = fields.Char('appid',default="1196a2f3-7eb0-9632-c866-8d05ad744379")
    publickey = fields.Char('公钥',default='#2*9De0(AC$Def.d')
    privatekey = fields.Char('私钥',default="58396aecb77f0b16")
    sid = fields.Char('请求的报文流水号',default=str(time.time()))
    input = fields.Text('输入值',default="{}")
    serviceid = fields.Char('服务ID',default="HQQYJBXX")
    nsrsbh = fields.Char('纳税人识别号',default='91310118MA1JLFH42X')

    @api.one
    def request(self):
        url = self.api_url
        inputstr = self.input
        inputmi = encrypt(inputstr, self.privatekey)
        json_encode = json.dumps({
            'appid': self.appid,
            'serviceid': self.serviceid,
            'sid': self.sid,
            'nsrsbh': self.nsrsbh,
            'input':inputmi
        })
        params = {
            "json": quote_plus(encrypt(json_encode, self.publickey))
        }
        res = requests.post(url,data=params)
        if res.status_code == 200:
            ret = res.json()
            if 'data' in ret:
                ret['data'] = json.loads(decrypt(ret['data'], privatekey))
            return ret
        else:
            return res.text

