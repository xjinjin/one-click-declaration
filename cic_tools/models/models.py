# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .dubbo_telnet import Dubbo
from sqlsoup import SQLSoup

class financeWizard(models.TransientModel):
    _name = "cic_tools.cic_finance"
    _description = "嘉商通总账系统接口工具向导"

    @api.model
    def get_table(self, tablename):
        db = SQLSoup("mysql+pymysql://cic_admin:159357a@{}:{}/cic_finance".format('192.168.10.11',3306))
        table = db.entity(tablename)
        records = table.all()
        res = [{key: val
                for key, val in record.__dict__.items()
                if not key.startswith('_')} for record in records]

        return res

    
    @api.model
    def get_fileProcessingAnalysisByPeriod(self, periodId):
        dubbo_conn = Dubbo('192.168.1.58',20889)
        dubbo_conn.set_encoding('GB18030')
        res = dubbo_conn.invoke('cn.ciccloud.ocr.recognition.service.OcrStatisticsService', 'fileProcessingAnalysisByPeriod', {'periodId':periodId})
        if res:
            if isinstance(res,list) and isinstance(res[1],str) and 'elapsed: ' in res[1]:
                res = eval(res[0].replace('null','None').replace('false','False').replace('true','True'))
        return res

    @api.model
    def get_ocr_recfiles(self, upload_date_start='',upload_date_end='',taxnum='',period_id=''):
        dubbo_conn = Dubbo('192.168.1.58',20889)
        dubbo_conn.set_encoding('GB18030')
        params = {'upload_date_start':upload_date_start,'upload_date_end':upload_date_end}
        if upload_date_start:
            params.update({'upload_date_start':upload_date_start})
        if upload_date_end:
            params.update({'upload_date_end':upload_date_end}) 
        if taxnum:
            params.update({'taxnum':taxnum})
        if period_id:
            params.update({'period_id':period_id})
        res = dubbo_conn.invoke('cn.ciccloud.ocr.recognition.service.FileMgmtService', 'queryRecFileWithPage', params)
        if res:
            if isinstance(res,list) and isinstance(res[1],str) and 'elapsed: ' in res[1]:
                res = eval(res[0].replace('null','None').replace('false','False').replace('true','True'))
        return res

    @api.model
    def get_duboo_data(self, server='192.168.1.58',port=20990, interface='', method='', params = {}):
        dubbo_conn = Dubbo(server,port)
        dubbo_conn.set_encoding('GB18030')
        if interface and method:
            res = dubbo_conn.invoke(interface, method, params)
        else:
            res = {}
        if res:
            if isinstance(res,list) and len(res)==2 and isinstance(res[1],str) and 'elapsed: ' in res[1]:
                res = eval(res[0].replace('null','None').replace('false','False').replace('true','True'))
        return res

    @api.model
    def get_declaration_data(self, TaxNum, DateStart,DateEnd):
        DateEnd = str(DateEnd)
        DateStart = str(DateStart)

        interface = "cn.ciccloud.finance.declaration.service.ApiService"
        Methods = {
            '财务报表' : 'queryFinanceReportFromFinance',  #财务报表
            '主表' : 'queryGrMainFromFinance',  #主表
            '附表一' : 'queryGrDetailOneFromFinance' , #附表一
            '附表二' : 'queryGrDetailTwoFromFinance'   # 附表二
        }
        params = '{"declareDateEnd":"%s 23:59:59", "taxnum":"%s", "declareDateStart":"%s 00:00:00"}'%(DateEnd,TaxNum,DateStart)


        new_data = {}

        for name , method in Methods.items():
            try:
                data = self.get_duboo_data(interface=interface, method=method, params=params)
            except Exception as e:
                data = {}
            if type(data) == list:
                continue
            if name == '财务报表':  #todo：财务报表年报的处理
                new_data['现金流量表'] = data.get('financeCash','')
                new_data['利润表'] = data.get('financeProfit','')
                new_data['资产负债表'] = data.get('financeBalance','')
            else:
                new_data[name] = data

        return new_data




