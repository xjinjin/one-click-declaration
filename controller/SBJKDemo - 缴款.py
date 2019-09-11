
# -*- coding: utf-8 -*-

from controller.ServicePostUtil import taxsbAPIWizard
import json

class SBJKDemo(object):

    ''' input：appKey,token,param
        transfer：taxsbAPIWizard
        output: response.json/response.text'''

    def __init__(self,nsrsbh = '', sbzlbh = '10101',nsqxdm = '',dqbm = '',ssqq = '2019-06-01',ssqz = '2019-06-30',
                 sbwj = '2019-06-30',je = '',yhzl = '',yhdm = '',yhzh = ''):
        self.param = {}
        self.param['nsrsbh'] = nsrsbh   # 必填
        self.param['sbzlbh'] = sbzlbh   # 必填 参考代码表  平台申报开放API规范2.0(1)文档
        self.param['nsqxdm'] = nsqxdm   # 纳税期限代码(江苏必填)
        self.param['dqbm'] = dqbm       # 地区编码(江苏必填)
        self.param['ssqq'] = ssqq       # 必填 税款所属期起
        self.param['ssqz'] = ssqz       # 必填 税款所属期止
        self.param['sbwj'] = sbwj       # 申报文件(湖南必填)
        self.param['je'] = je           # 金额 必填
        self.param['yhzl'] = yhzl       # 银行种类(湖南必填)
        self.param['yhdm'] = yhdm       # 银行代码(湖南必填)
        self.param['yhzh'] = yhzh       # 银行账号(湖南必填)

    def void_main(self,appKey,token):
        res = taxsbAPIWizard().post(json.dumps(self.param),appKey,token)
        return res

if __name__ == '__main__':
    pass
