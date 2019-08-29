# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime, timedelta
from datetime import date
from babel.dates import format_datetime, format_date
from odoo import api, models, fields, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime
from datetime import date, timedelta

class SalesPersonTarget(models.Model):
    _name = 'sales.dashboard'


    @api.model
    def _update_date(self):
        ''' This method is called from a cron job. '''
        for data in self.search([]):
            data.write({'today_date' : datetime.today()})

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id


    @api.one
    def _get_sale_total_iqd(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        total_amount = 0
        SaleOrder = self.env['sale.order']
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            total_amount = sum([data.amount_total for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59'),('pricelist_id.currency_id.name','=','IQD')])])
        else:
            date = str(self.today_date)
            total_amount = sum([data.amount_total for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59'),('pricelist_id.currency_id.name','=','IQD')])])
        self.total_sale_order_iqd = total_amount 

    @api.one 
    def _get_sale_total(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        SaleOrder = self.env['sale.order']
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            total_amount = sum([data.amount_total for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59'),('pricelist_id.currency_id.name','=','USD')])])
        else:
            date = str(self.today_date)
            total_amount = sum([data.amount_total for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59'),('pricelist_id.currency_id.name','=','USD')])])
        self.total_sale_order = total_amount


    @api.one
    def _get_profit_amount(self):
        total_purchase_amount = 0
        total_sale_amount = 0
        SaleOrder = self.env['sale.order']
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    total_purchase_amount += (line.product_uom_qty * line.product_id.standard_price)
                    total_sale_amount += (line.product_uom_qty * line.price_unit)

        else:
            date = str(self.today_date)
            for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    total_purchase_amount += (line.product_uom_qty * line.product_id.standard_price)
                    total_sale_amount += (line.product_uom_qty * line.price_unit)

        self.total_proit = (total_sale_amount - total_purchase_amount)


    @api.one
    def _get_total_qty(self):
        total_qty = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        SaleOrder = self.env['sale.order']
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')]):
                total_qty = sum([line.product_uom_qty for line in self.env['sale.order.line'].search([('order_id','=',data.id)])])
        else :
            date = str(self.today_date)
            for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')]):
                total_qty = sum([line.product_uom_qty for line in self.env['sale.order.line'].search([('order_id','=',data.id)])])
        self.total_qty = total_qty

    @api.one
    def _total_sale(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        SaleOrder = self.env['sale.order']
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            search_id = SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')])
            self.total_sale = len(search_id)
        else:
            date = str(self.today_date)
            search_id = SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')])

            self.total_sale = len(search_id)
            self.sum_waiting = len(search_id)

    @api.one
    def _total_invoice(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            list_id = [data.reconciled_invoice_ids.id for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date)])]
        else:
            date = str(self.today_date)
            list_id = [data.reconciled_invoice_ids.id for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date)])]
        self.total_invoices = len(list_id)

    @api.one
    def _total_invoice_amount(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            account_payment = self.env['account.payment']
            total_amount = sum([data.amount for data in account_payment.search([('currency_id.name','=','USD'),('payment_date','>=',date),('payment_date','<=',date)])])
            self.total_paid_invoice = total_amount
        else:
            date = str(self.today_date)
            total_amount = sum([data.amount for data in account_payment.search([('currency_id.name','=','USD'),('payment_date','>=',date),('payment_date','<=',date)])])
            self.total_paid_invoice = total_amount

    @api.one
    def _total_invoice_amount_iqd(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        account_payment = self.env['account.payment']
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            total_amount = sum([data.amount for data in account_payment.search([('currency_id.name','=','IQD'),('payment_date','>=',date),('payment_date','<=',date)])])
            search_id = self.env['res.currency'].search([('name','=','IQD')])
            self.total_paid_invoice_iqd = total_amount

        else:
            date = str(self.today_date)
            total_amount = sum([data.amount for data in account_payment.search([('currency_id.name','=','IQD'),('payment_date','>=',date),('payment_date','<=',date)])])
            search_id = self.env['res.currency'].search([('name','=','IQD')])
            self.total_paid_invoice_iqd = total_amount


    @api.one
    def _get_iqd_symbol(self):
        search_id = self.env['res.currency'].search([('name','=','IQD')])
        self.char_currency = search_id.symbol

    total_qty = fields.Integer(compute="_get_total_qty")
    total_proit = fields.Integer(compute="_get_profit_amount")
    total_sale_order_iqd = fields.Integer(compute="_get_sale_total_iqd")
    total_sale_order = fields.Integer(compute="_get_sale_total")
    today_date = fields.Date('Order Date', default=fields.Date.context_today)
    char_currency = fields.Char('_get_iqd_symbol')
    total_paid_invoice = fields.Integer(compute="_total_invoice_amount")
    total_paid_invoice_iqd = fields.Integer(compute="_total_invoice_amount_iqd")
    sum_waiting = fields.Integer(compute="_total_sale")
    number_waiting = fields.Integer(compute="_total_sale")
    total_sale = fields.Integer(compute="_total_sale")
    total_invoices = fields.Integer(compute="_total_invoice")
    name = fields.Char('Sales Team', required=True, translate=True)
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the sales team without removing it.")
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    color = fields.Integer(string='Color Index', help="The color of the team")
    currency_id = fields.Many2one('res.currency', string='Currency',
        default=_default_currency, track_visibility='always')

    @api.multi
    def sale_order(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        SaleOrder = self.env['sale.order']
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            search_id = SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                      ('date_order','<=',date + ' 23:59:59')])
            return {
                'name': _('Sale Order'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', search_id.ids)],
                }
        else:
            date = str(self.today_date)
            search_id = SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                      ('date_order','<=',date + ' 23:59:59')])
            return {
                'name': _('Sale Order'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', search_id.ids)],
                }

    @api.multi
    def sale_order_line(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        SaleOrder = self.env['sale.order']
        sale_order_line = self.env['sale.order.line']
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                      ('date_order','<=',date + ' 23:59:59')]):
                list_id = [line.id for line in sale_order_line.search([('order_id','=',data.id)])]

            return {
                'name': _('Sale Order Line'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'view_id': False,
                'context' : "{'search_default_product': 1}",
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', list_id)],
                }

        else:
            date = str(self.today_date)
            for data in SaleOrder.search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                      ('date_order','<=',date + ' 23:59:59')]):
                list_id = [line.id for line in sale_order_line.search([('order_id','=',data.id)])]

            return {
                'name': _('Sale Order Line'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order.line',
                'view_id': False,
                'context' : "{'search_default_product': 1}",
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', list_id)],
                }

    @api.multi
    def sales_person_target_dashboard(self):
        return {
            'name': _('Sales Person'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sales.person.target',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('user_id', '=', self.user_id.id),
                       ('active', '=', True)],
        }

    @api.multi
    def sales_invoice(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        account_invoice = self.env['account.payment']
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            list_id = [data.reconciled_invoice_ids.id for data in account_invoice.search([('payment_date','>=',date),('payment_date','<=',date)])]
                views = [(self.env.ref('account.invoice_tree').id, 'tree'), (self.env.ref('account.invoice_form').id, 'form')]
                return {
                    'name': _('Paid Invoices'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.invoice',
                    'view_id': False,
                    'views': views,
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', list_id)],
                }
        else:
            date = str(self.today_date)
            list_id = [data.reconciled_invoice_ids.id for data in account_invoice.search([('payment_date','>=',date),('payment_date','<=',date)])]
                views = [(self.env.ref('account.invoice_tree').id, 'tree'), (self.env.ref('account.invoice_form').id, 'form')]
                return {
                    'name': _('Paid Invoices'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.invoice',
                    'view_id': False,
                    'views': views,
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', list_id)],
                }
            