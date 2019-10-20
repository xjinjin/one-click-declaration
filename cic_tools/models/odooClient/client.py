#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inspired by jsonrpc-client, is a json-rpc client for odoo .
jsonrpc-client Homepage and documentation: https://github.com/lerry/jsonrpc-client
Copyright (c) 2015, Lerry.
License: MIT (see LICENSE for details)
"""
import requests
import sys, traceback
from uuid import uuid4

from json import dumps, loads

class ConnectorError(BaseException):
    """Exception raised by the ``odoorpc.rpc`` package."""
    def __init__(self, message, odoo_traceback=None):
        self.message = message
        self.odoo_traceback = odoo_traceback

class Client(object):
    def __init__(self, url, **kwargs):
        self.url = url
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        if kwargs.get("headers"):
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers
        self.kwargs = kwargs
        self.version = kwargs.pop('version', None)
        self.request = requests.Session()

    def _make_data(self, _method, *args, **kwargs):
        if kwargs:
            params = kwargs
            if args:
                params["__args"] = args
        else:
            params = args
        return {
            "jsonrpc": "2.0",
            "method": bytes(_method),
            "params": params,
            "id": bytes(uuid4()),
        }

    def _fetch(self, _method, *args, **kwargs):
        data = self._make_data(_method, *args, **kwargs)
        req = self.request.post(self.url, data=dumps(data).encode(), **self.kwargs)
        if req.status_code == 200:
            return self._parse_result(data, req.text)
        else:
            msg = "\nHTTP Error: %s\n %s" % (req.status_code, req.content)
            raise Exception(msg)

    def _parse_result(self, request, text):
        data = loads(text)
        if request["id"] != data["id"]:
            msg = "\nError: \n  id not match"
        #elif "error" in data:
        #    msg = "\nREMOTE Server Error: \n  " + str(data["error"])
        #elif "result" in data:
        #    return data["result"]
        else:
            return data
        raise Exception(msg)

    def __getattr__(self, key):
        
        def _(*args, **kwargs):
            return self._fetch(key, *args, **kwargs)
        return _

