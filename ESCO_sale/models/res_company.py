# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class res_company(models.Model):
    _inherit = "res.company"
    
    force_restrict_sale_stock = fields.Boolean('Force Restrict Sales Stock')