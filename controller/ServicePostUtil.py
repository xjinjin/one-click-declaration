# -*- coding: utf-8 -*-

from hashlib import sha256
import hmac
import requests
import json


class taxsbAPIWizard(object):
    '''
        input: content,appkey,token
        output: response.json/response.text
    '''
    _name = "cic_taxsb.api"
    _description = "嘉商通总账系统申报接口API向导"

    def __init__(self,url = 'http://211.151.124.80:6006/remote/callServer'):
        # 'http://101.200.62.94:9187/remote/callServer'
        # 'http://211.151.124.80:6006/remote/callServer'
        self.url = url

    def post(self,content,appkey,token ):
        params = {
            "appKey": appkey,
            "token": hmac.new(bytes(token, 'utf-8'), msg=bytes(content,'utf-8'), digestmod=sha256).hexdigest(),
            "jsonData": content
        }
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        # headers = {'Content-type':'application/json;charset=UTF-8'} # 文档和demo又争议，以demo为准
        res = requests.post(self.url, data=params, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            return res.text
        # return res

if __name__ == '__main__':
    pass