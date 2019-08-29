# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockQuant(models.Model):
    _inherit = "stock.quant"
    
    product_brand_id = fields.Many2one(related="product_id.product_brand_id", string="Brand", store=True)
    manufacturing_of_country = fields.Many2one('res.country',string="Manufacturing Of Country")


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    product_brand_id = fields.Many2one(related="product_id.product_brand_id", string="Brand", store=True)
    manufacturing_of_country = fields.Many2one('res.country',string="Manufacturing Of Country")
   
    