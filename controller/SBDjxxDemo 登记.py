# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import base64
import json

class SBDjxxDemo(object):
    # 申报-登记信息
    '''(最优先调用接口)申报提交之前必须调用登记接口'''

    # xmlStr  登记报文:各家公司需要自己收集信息,分地区字段可能不一样
    # xmlStr = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><jsds_jbxxVO><sbbinfo><nsrsbh>91320214MA1NYKMBXK</nsrsbh><qymc>无锡品凡自动化设备有限公司</qymc><sbname>jbxx</sbname><dqbm>32</dqbm><cwlxr>姜不凡</cwlxr><cwlxrlxfs>15961853615</cwlxrlxfs><dscsdlmm>123456</dscsdlmm><dsdlfs>2</dsdlfs><dsdlmm>Jj111111</dsdlmm><dsdlyhm>91320214MA1NYKMBXK</dsdlyhm><gscamm>123456</gscamm><gsdlfs>2</gsdlfs><gsnsmm>Jj111111</gsnsmm><gsnsrsbh>91320214MA1NYKMBXK</gsnsrsbh><gsnsyhm>91320214MA1NYKMBXK</gsnsyhm><kjzd>1</kjzd><nsrzgdm>001</nsrzgdm><qyyf>09</qyyf><qynf>2019</qynf></sbbinfo></jsds_jbxxVO>'
    def __init__(self):
        self.nsrsbh = '91320214MA1NYKMBXK'         # 申报的纳税人识别号 必须传
        self.qymc = '无锡品凡自动化设备有限公司'           # 企业名称                          必须传
        self.sbname = 'jbxx'         # 基本信息接口 【固定值jbxx】       必须传
        self.dqbm = '32'           # 地区编码【参考地区编码 平台申报开放API规范2.0(1)文档】 必须传
        self.cwlxr = '姜不凡'          # 财务联系人          【江苏必须传】
        self.cwlxrlxfs = '15961853615'      # 财务联系人联系电话  【江苏必须传】

        self.dscsdlmm = '123456'       # 地税CA密码
        self.dsdlfs = '2'         # 地税登录方式 1 CA(目前不支持线上，需要联系运维人员) 2 用户名密码
        self.dsdlmm = 'Jj111111'         # 地税登录密码
        self.dsdlyhm = '91320214MA1NYKMBXK'        # 地税登录名

        self.gscamm = '123456'         # 国税CA密码 【(目前不支持线上，需要联系运维人员) 】
        self.gsdlfs = '2'         # 国税登录方式 【1: CA(目前不支持线上，需要联系运维人员) 2: 用户名密码(税号)  3:实名账号(江苏无需此类型) 】
        self.gsnsmm = 'Jj111111'         # 国税登录密码                      必须传
        self.gsnsrsbh = '91320214MA1NYKMBXK'       # 纳税人识别号                      必须传
        self.gsnsyhm = '91320214MA1NYKMBXK'        # 国税登录名                        必须传

        self.kjzd = '1'           # 必须传 (1-9 代表不同准则 据体参照文档)
        self.nsrzgdm = '001'        # 纳税资格代码 【001增值税一般纳税人/101增值税小规模纳税人】 必须传
        self.qyyf = '08'           # 启用月份(必填) 【系统(当前)月份】          必须传
        self.qynf = '2019'           # 启用年份(必填) 【系统(当前)年份】          必须传

        self.xmlStr = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><jsds_jbxxVO><sbbinfo><nsrsbh>{}</nsrsbh>' \
                      '<qymc>{}</qymc><sbname>{}</sbname><dqbm>{}</dqbm><cwlxr>{}</cwlxr><cwlxrlxfs>{}</cwlxrlxfs>' \
                      '<dscsdlmm>{}</dscsdlmm><dsdlfs>{}</dsdlfs><dsdlmm>{}</dsdlmm><dsdlyhm>{}</dsdlyhm>' \
                      '<gscamm>{}</gscamm><gsdlfs>{}</gsdlfs><gsnsmm>{}</gsnsmm><gsnsrsbh>{}</gsnsrsbh>' \
                      '<gsnsyhm>{}</gsnsyhm><kjzd>{}</kjzd><nsrzgdm>{}</nsrzgdm><qyyf>{}</qyyf><qynf>{}</qynf>' \
                      '</sbbinfo></jsds_jbxxVO>'.format(self.nsrsbh, self.qymc, self.sbname, self.dqbm, self.cwlxr,
                                                        self.cwlxrlxfs,self.dscsdlmm,self.dsdlfs,self.dsdlmm,
                                                        self.dsdlyhm ,self.gscamm ,self.gsdlfs ,self.gsnsmm ,
                                                        self.gsnsrsbh ,self.gsnsyhm ,self.kjzd ,self.nsrzgdm ,
                                                        self.qyyf ,self.qynf)
        self.param = {}
        self.bizXml = base64.b64encode(self.xmlStr.encode('utf-8')).decode("utf-8")
        self.param['bizXml'] = self.bizXml   # bizXml=登记信息xml报文 加密之后字符串

    def void_main(self,appKey,token):
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        return res

if __name__ == '__main__':
    # pass
    appKey = '68c8c236c8484b35b149019d590ff0b0'
    token = '7f182e426e1a5508c40bbdfa'
    res = SBDjxxDemo().void_main(appKey,token)
    print(res)
    # {'status': 200, 'code': 'B1000', 'msg': None, 'stackTrace': None, 'data': '登记成功'}