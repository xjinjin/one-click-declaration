
# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import json
import time

class SBInitDemo(object):

    ''' input：appKey,token,param
        transfer：taxsbAPIWizard
        output: response.json/response.text'''

    def __init__(self,nsrsbh = '91320214MA1NYKMBXK', sbzlbh = '10101',skssqq = '2019-08-01',
                 skssqz = '2019-08-31',nsqxdm = '1',sssq = '2019-09'):
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
        # {"nsrsbh": "91320214MA1NYKMBXK", "sbzlbh": "10101", "skssqq": "2019-08-01", "skssqz": "2019-08-31", "nsqxdm": "1", "sssq": "2019-08"}
        return res

class AfterSBInitDemo(object):

    def __init__(self,nsrsbh = '91320214MA1NYKMBXK', sbzlbh = '10101',skssqq = '2019-08-01',
                 skssqz = '2019-08-31',nsqxdm = '1',sssq = '2019-09'):
        self.param = {}
        self.param['nsrsbh'] = nsrsbh   # 纳税人识别号
        self.param['sbzlbh'] = sbzlbh   # 申报种类编码.参考代码表  平台申报开放API规范2.0(1)文档
        self.param['skssqq'] = skssqq   # 税款所属期起
        self.param['skssqz'] = skssqz   # 税款所属期止
        self.param['sssq'] = sssq       # 税款所属期
        self.param['nsqxdm'] = nsqxdm   # 纳税期限代码


    def void_main(self,appKey,token):
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        # print(json.dumps(self.param))
        # {"nsrsbh": "91320214MA1NYKMBXK", "sbzlbh": "10101", "skssqq": "2019-08-01", "skssqz": "2019-08-31", "sssq": "2019-09", "nsqxdm": "1"}
        return res

if __name__ == '__main__':


    # pass
    # appKey = '8537af01c6034b9b9de71b7dabbcd935'
    # token = 'a671d83d4e614c25e17f36dd'
    # res = SBInitDemo().void_main(appKey,token)
    # print(res)
    # {'status': 200, 'code': 'C0000', 'msg': '初始化成功', 'stackTrace': None, 'data': '【江苏】添加初始化成功,正常12分钟左右(任务多的时间长些),之后请通过申报-初始化数据获取接口查询！'}

    # time.sleep(13*60) #  江苏地区：先调用SBInitDemo，等12分钟，在调用AfterSBInitDemo

    after_appKey = '060fdcfa94aa4d8da031d5cc2b755ae4'
    after_token = 'f1f1683a36d0af2e9570bbd6'
    after_res = AfterSBInitDemo().void_main(after_appKey,after_token)
    print(after_res)

    # {'status': 500, 'code': 'C1000', 'msg': '该税号所在地区初始化服务暂未开通。', 'stackTrace': None, 'data': None}