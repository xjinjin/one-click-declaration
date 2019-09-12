# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import base64
import json

class SBStatusDemo(object):
    # 申报-申报状态
    '''申报结果查询接口'''

    ''' input：appKey,token,param
        transfer：taxsbAPIWizard
        output: response.json/response.text'''

    def __init__(self,
                 lsh = '',
                 xmlStr = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><jsds_sbztxxVO><sbbinfo><sbzlbh>10101</sbzlbh><nsrsbh>913201040802573908</nsrsbh><sbname>sbzt</sbname><kjnd>2019</kjnd><kjqj>03</kjqj></sbbinfo></jsds_sbztxxVO>'
                 ):
        # self.xmlStr = xmlStr
        self.param = {}
        bizXml = base64.b64encode(xmlStr.encode('utf-8')).decode("utf-8")
        self.param['bizXml'] = bizXml   # 申报状态查询xml报文 加密之后字符串
        self.param['lsh'] = lsh         # 申报提交得流水号 必传

    def void_main(self,appKey,token):
        # self.appKey = "eee8a281ee2b4553aa702c91db375a7b"
        # self.token = "c3647ad82ff72cbc09a55977"
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        return res

if __name__ == '__main__':
    pass
    # print(SBStatusDemo().param)