
# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import json

class SBSubmitDemo(object):

    ''' input：appKey,token,param
        transfer：taxsbAPIWizard
        output: response.json/response.text'''

    def __init__(self,nsrsbh = '913201040802573908', sbzlbh = '10101',skssqq = '2019-04-01', skssqz = '2019-04-30',
                 sssq = '2019-04'):
        self.param = {}
        self.param['nsrsbh'] = nsrsbh
        self.param['sbzlbh'] = sbzlbh
        self.param['skssqq'] = skssqq
        self.param['skssqz'] = skssqz
        self.param['sssq'] = sssq

    def void_main(self,appKey,token):
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        return res

if __name__ == '__main__':
    pass
    # a = SBInitDemo()
    # a.param['test'] = 'test'
    # print(a.param)