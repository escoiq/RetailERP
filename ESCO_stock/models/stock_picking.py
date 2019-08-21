# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class Picking(models.Model):
    _inherit = "account.invoice"

    @api.one 
    def _get_account_id(self):
        if self.partner_id.customer:
            self.account_id = self.partner_id.property_account_receivable_id.id
        elif self.partner_id.supplier:
            self.account_id = self.partner_id.property_account_payable_id.id

    account_id = fields.Many2one('account.account', string='Account',
        readonly=True, states={'draft': [('readonly', False)]},
        domain=[('deprecated', '=', False)], help="The partner account used for this invoice.",compute="_get_account_id")
   
class Picking(models.Model):
    _inherit = "stock.picking"
    
    @api.multi
    def action_done(self):
        result = super(Picking, self).action_done()
        for pick in self:
            pick.create_vendor_bill_on_validate()
        return result
            
    
    @api.multi
    def create_vendor_bill_on_validate(self):
        self.ensure_one()
        if self.origin:
            po = self.env['purchase.order'].search([('name','=',self.origin)])
            if po:
                inv_context = {
                    'type': 'in_invoice',
                    'default_purchase_id': po.id,
                    'default_currency_id': po.currency_id.id,
                    'default_company_id': po.company_id.id,
                    'company_id': po.company_id.id
                }
                values = {
                    'type': 'in_invoice',
                    'purchase_id': po.id,
                    'currency_id': po.currency_id.id,
                    'company_id': po.company_id.id,
                    'account_id' : po.partner_id.property_account_payable_id.id
                }
                invoice_id = self.env['account.invoice'].with_context(inv_context).create(values)
                invoice_id.purchase_order_change()

        return True