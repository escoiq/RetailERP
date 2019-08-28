# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id:
            self.name = self.product_id.get_name_for_line()
        return res