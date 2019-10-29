#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'pyhunterpig'
__version__ = '0.1.0'
__license__ = 'MIT'

__all__ = ['ODOO', 'error']

import logging

from .odoo import ODOO
from . import error

logging.getLogger(__name__).addHandler(logging.NullHandler())
