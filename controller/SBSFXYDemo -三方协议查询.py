
# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import json

class SBSFXYDemo(object):
    # 申报-查询三方协议信息
    '''三方协议，支持湖南、贵州地区'''

    ''' input：appKey,token,param
        transfer：taxsbAPIWizard
        output: response.json/response.text'''

    def __init__(self,nsrsbh = ''):
        self.param = {}
        self.param['nsrsbh'] = nsrsbh

    def void_main(self,appKey,token):
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        return res

if __name__ == '__main__':
    pass
