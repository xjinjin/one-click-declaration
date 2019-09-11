
# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import json

class SBZFDemo(object):

    ''' input：appKey,token,param
        transfer：taxsbAPIWizard
        output: response.json/response.text'''

    def __init__(self,lsh = '',nsrsbh = '913201040802573908',sbzlbh = '10101',
                 skssqq = '2019-04-01',skssqz = '2019-04-30',sssq = '2019-04'):
        self.param = {}
        self.param['lsh'] = lsh         # 申报成功流水号
        self.param['nsrsbh'] = nsrsbh
        self.param['sbzlbh'] = sbzlbh   # 参考代码表  平台申报开放API规范2.0(1)文档
        self.param['skssqq'] = skssqq   # 税款所属期起
        self.param['skssqz'] = skssqz   # 税款所属期止
        self.param['sssq'] = sssq       # 税款所属期

    def void_main(self,appKey,token):
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        return res

if __name__ == '__main__':
    pass
