# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import base64
import json

class SBDjxxDemo(object):
    ''' input：appKey,token,param
        transfer：taxsbAPIWizard
        output: response.json/response.text'''

    # xmlStr  登记报文:各家公司需要自己收集信息,分地区字段可能不一样
    def __init__(self,
                 xmlStr = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><jsds_jbxxVO><sbbinfo><nsrsbh>91320214MA1NYKMBXK</nsrsbh><qymc>无锡品凡自动化设备有限公司</qymc><sbname>jbxx</sbname><dqbm>32</dqbm><cwlxr>姜不凡</cwlxr><cwlxrlxfs>15961853615</cwlxrlxfs><dscsdlmm>123456</dscsdlmm><dsdlfs>2</dsdlfs><dsdlmm>Jj111111</dsdlmm><dsdlyhm>91320214MA1NYKMBXK</dsdlyhm><gscamm>123456</gscamm><gsdlfs>2</gsdlfs><gsnsmm>Jj111111</gsnsmm><gsnsrsbh>91320214MA1NYKMBXK</gsnsrsbh><gsnsyhm>91320214MA1NYKMBXK</gsnsyhm><kjzd>1</kjzd><nsrzgdm>001</nsrzgdm><qyyf>09</qyyf><qynf>2019</qynf></sbbinfo></jsds_jbxxVO>'
                 ):
        self.xmlStr = xmlStr
        self.param = {}
        self.bizXml = base64.b64encode(self.xmlStr.encode('utf-8')).decode("utf-8")
        self.param['bizXml'] = self.bizXml   # bizXml=登记信息xml报文 加密之后字符串

    def void_main(self,appKey,token):
        # url = 'http://211.151.124.80:6006/remote/callServer'
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        return res

if __name__ == '__main__':
    # pass
    appKey = '68c8c236c8484b35b149019d590ff0b0'
    token = '7f182e426e1a5508c40bbdfa'
    res = SBDjxxDemo().void_main(appKey,token)
    print(res)
    # {'status': 200, 'code': 'B1000', 'msg': None, 'stackTrace': None, 'data': '登记成功'}