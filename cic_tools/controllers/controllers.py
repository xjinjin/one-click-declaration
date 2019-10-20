# -*- coding: utf-8 -*-
from odoo import http

def getmsg(url):
    temp_msg = ''
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        start_index = html.find('公司类型')
        start_index = html.find('<td',start_index)
        start_index = html.find('>',start_index)
        end_index = html.find('</td',start_index)
        temp_msg = html[start_index+1:end_index]
    return temp_msg

def fetch_tianyancha_msg(companyname):
        key = companyname
        url = 'https://www.tianyancha.com/search'
        response = requests.get(url,data={'key':key})
        if response.status_code == 200:
            html = response.text
            start_index = html.find('tyc-event-ch="CompanySearch.Company"')
            start_index = html.find('href="', start_index)+6
            end_index = html.find('"',start_index)
            msg_url = html[start_index:end_index]
            print(msg_url)
        tianyancha_msg = getmsg(msg_url)
        return tianyancha_msg


# class YzContract(http.Controller):
#     @http.route('/yz_contract/yz_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/yz_contract/yz_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('yz_contract.listing', {
#             'root': '/yz_contract/yz_contract',
#             'objects': http.request.env['yz_contract.yz_contract'].search([]),
#         })

#     @http.route('/yz_contract/yz_contract/objects/<model("yz_contract.yz_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('yz_contract.object', {
#             'object': obj
#         })