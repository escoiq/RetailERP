# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.one
    def _compute_payment(self):
        search_id = self.env['account.payment'].search([('partner_id','=',self.id)])
        self.payment_count = len(search_id)

    payment_count = fields.Integer('assignment',compute="_compute_payment")

    @api.multi
    def action_open_payment(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_payments')
        list_view_id = self.env.ref('account.view_account_payment_tree').id
        form_view_id = self.env.ref('account.view_account_payment_form').id

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'res_model': action.res_model,
        }
        search_ids = self.env['account.payment'].search([('partner_id','=',self.id)])
        if len(search_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % search_ids.ids
        elif len(search_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = search_ids.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.one
    def _get_balance(self):
        """Get balance amount from inbound payment - outbound payment """
        account_payment = self.env['account.payment']
        send_amont = sum([data.payment_balance for data in account_payment.search([('partner_id','=',self.id),('payment_type','=','outbound')])])
        receive_amount = sum([data.payment_balance for data in account_payment.search([('partner_id','=',self.id),('payment_type','=','inbound')])])
        self.balance_payment = (receive_amount - send_amont)

    @api.one
    def _total_invoice(self):
        search_id = self.env['account.invoice'].search([('partner_id','=',self.id)])
        self.total_invoice = len(search_id)

    @api.one
    def _total_amount(self):
        self.total_amount = sum([data.amount_total for data in self.env['account.invoice'].search([('partner_id','=',self.id)])])

    @api.one
    def _amount_due(self):
        self.amount_due = sum([data.residual_signed for data in self.env['account.invoice'].search([('partner_id','=',self.id)])])

    total_invoice = fields.Integer('Total Invoice', compute="_total_invoice")
    total_amount = fields.Float("Amount of Invoices", compute="_total_amount")
    amount_due = fields.Float("Due amount", compute="_amount_due")
    balance_payment = fields.Float("Balance", compute="_get_balance")

class account_payment(models.Model):
    _inherit = "account.payment"

    payment_balance = fields.Monetary(compute='_compute_payment_balance', string="Unapplied Balance",store="True", 
                                      help="What remains after deducting amounts already applied to close or reduce invoice balances.")

    @api.one
    @api.depends('invoice_ids','move_line_ids.matched_debit_ids','move_line_ids.matched_credit_ids')
    def _compute_payment_balance(self):
        ids = []
        total_amount = 0.0
        for aml in self.move_line_ids:
            if aml.account_id.reconcile:
                ids.extend([r.debit_move_id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id for r in aml.matched_credit_ids])
        for ml in ids:
            if self.payment_type == 'inbound':
                total_amount += ml.debit - ml.amount_residual
            else:
                total_amount += ml.credit - ml.amount_residual
        if total_amount > 0.0:
            set_amount = self.amount - total_amount
            if set_amount > 0.0:
                self.payment_balance = set_amount
            else:
                self.payment_balance = 0.0
        else:
            self.payment_balance = 0.0

        if not self.has_invoices:
            self.payment_balance = self.amount

