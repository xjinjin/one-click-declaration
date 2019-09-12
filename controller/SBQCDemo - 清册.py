
# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import json

class SBQCDemo(object):
    # 申报-申报清册 江苏不支持
    '''查询当前纳税人能报的税种（没有xml 报文）'''

    def __init__(self):
        self.param = {}
        self.param['nsrsbh'] = '91320214MA1NYKMBXK'         # 申报的纳税人识别号 必须传
        self.param['sbzlbh'] = '10101'   # 申报种类,参考代码表  平台申报开放API规范2.0(1)文档
        self.param['skssqq'] = '2019-08-01'   # 税款所属期起
        self.param['skssqz'] = '2019-08-31'   # 税款所属期止
        self.param['sssq'] = '2019-08'       # 税款所属期

    def void_main(self,appKey,token):
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        return res

if __name__ == '__main__':
    # pass
    appKey = '71f334d5e3c6473ba7f286986fef1b11'
    token = 'aa8baa3655ccefc2152801d2'
    after_res = SBQCDemo().void_main(appKey,token)
    print(after_res)