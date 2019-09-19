# -*- coding: utf-8 -*-
from odoo import http



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