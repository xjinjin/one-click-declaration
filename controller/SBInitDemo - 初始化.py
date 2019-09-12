
# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import json

class SBInitDemo(object):

    ''' input：appKey,token,param
        transfer：taxsbAPIWizard
        output: response.json/response.text'''

    def __init__(self,nsrsbh = '91320214MA1NYKMBXK', sbzlbh = '10101',skssqq = '2019-09-01',
                 skssqz = '2019-09-30',nsqxdm = '1',sssq = '2019-09'):
        self.param = {}
        self.param['nsrsbh'] = nsrsbh   # 纳税人识别号
        self.param['sbzlbh'] = sbzlbh   # 申报种类编码.参考代码表  平台申报开放API规范2.0(1)文档
        self.param['skssqq'] = skssqq   # 税款所属期起
        self.param['skssqz'] = skssqz   # 税款所属期止
        self.param['nsqxdm'] = nsqxdm   # 纳税期限代码
        self.param['sssq'] = sssq       # 税款所属期

    def void_main(self,appKey,token):
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        # print(json.dumps(self.param))
        return res

if __name__ == '__main__':
    # pass
    appKey = '8537af01c6034b9b9de71b7dabbcd935'
    token = 'a671d83d4e614c25e17f36dd'
    res = SBInitDemo().void_main(appKey,token)
    print(res)