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
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.one
    def _get_invoice_name(self):
        # self.invoice_name = self.reconciled_invoice_ids.number
        name = False
        for data in self.reconciled_invoice_ids:
            name = data.number
        self.invoice_name = name


    @api.one
    def _get_invoice_date(self):
        # self.date_invoice = self.reconciled_invoice_ids.date_invoice
        date = False
        for data in self.reconciled_invoice_ids:
            date = data.date_invoice
        self.invoice_name = date
        
    invoice_name = fields.Char(string="Invoice name",compute="_get_invoice_name")
    date_invoice = fields.Date(string="Invoice Date",compute="_get_invoice_date")

class SalesPersonTarget(models.Model):
    _name = 'sales.dashboard'
    _description = 'Sales Dashboard'


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
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59'),('pricelist_id.currency_id.name','=','IQD')]):
                total_amount += data.amount_total
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date_from + ' 00:00:00'),
                                                  ('date_order','<=',date_to + ' 23:59:59'),('pricelist_id.currency_id.name','=','IQD')]):
                total_amount += data.amount_total
        else:
            date = str(self.today_date)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59'),('pricelist_id.currency_id.name','=','IQD')]):
                total_amount += data.amount_total
        self.total_sale_order_iqd = total_amount 

    @api.one 
    def _get_sale_total(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59'),('pricelist_id.currency_id.name','=','USD')]):
                total_amount += data.amount_total
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date_from + ' 00:00:00'),
                                                  ('date_order','<=',date_to + ' 23:59:59'),('pricelist_id.currency_id.name','=','USD')]):
                total_amount += data.amount_total   
        else:
            date = str(self.today_date)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59'),('pricelist_id.currency_id.name','=','USD')]):
                total_amount += data.amount_total 
        self.total_sale_order = total_amount


    @api.one
    def _get_profit_amount(self):
        total_purchase_amount = 0
        total_sale_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    total_purchase_amount += (line.product_uom_qty * line.product_id.standard_price)
                    total_sale_amount += (line.product_uom_qty * line.price_unit)

        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date_from + ' 00:00:00'),
                                                  ('date_order','<=',date_to + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    total_purchase_amount += (line.product_uom_qty * line.product_id.standard_price)
                    total_sale_amount += (line.product_uom_qty * line.price_unit)

        else:
            date = str(self.today_date)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
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
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    total_qty += line.product_uom_qty

        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date_from + ' 00:00:00'),
                                                  ('date_order','<=',date_to + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    total_qty += line.product_uom_qty

        else :
            date = str(self.today_date)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    total_qty += line.product_uom_qty
        self.total_qty = total_qty

    @api.one
    def _total_sale(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            search_id = self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')])
            self.total_sale = len(search_id)
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            search_id = self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date_from + ' 00:00:00'),
                                                  ('date_order','<=',date_to + ' 23:59:59')])
            self.total_sale = len(search_id)

        else:
            date = str(self.today_date)
            search_id = self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                  ('date_order','<=',date + ' 23:59:59')])

            self.total_sale = len(search_id)
            self.sum_waiting = len(search_id)

    @api.one
    def _total_invoice(self):
        list_id = []
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','inbound')]):
                for inner_data in data.reconciled_invoice_ids:
                    list_id.append(inner_data.id) 
 
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['account.payment'].search([('payment_date','>=',date_from),('payment_date','<=',date_to),('payment_type','=','inbound')]):
                for inner_data in data.reconciled_invoice_ids:
                    list_id.append(inner_data.id) 
        else:
            date = str(self.today_date)
            for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','inbound')]):
                for inner_data in data.reconciled_invoice_ids:
                    list_id.append(inner_data.id) 
        self.total_invoices = len(list_id)


    @api.one
    def _total_expense(self):
        list_id = []
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','outbound')]):
                for inner_data in data.reconciled_invoice_ids:
                    list_id.append(inner_data.id) 
 
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['account.payment'].search([('payment_date','>=',date_from),('payment_date','<=',date_to),('payment_type','=','outbound')]):
                for inner_data in data.reconciled_invoice_ids:
                    list_id.append(inner_data.id) 
        else:
            date = str(self.today_date)
            for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','outbound')]):
                for inner_data in data.reconciled_invoice_ids:
                    list_id.append(inner_data.id) 
 
        self.total_expense = len(list_id)

    @api.one
    def _total_invoice_amount(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['account.payment'].search([('currency_id.name','=','USD'),('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','inbound')]):
                total_amount += data.amount
            self.total_paid_invoice = total_amount
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['account.payment'].search([('currency_id.name','=','USD'),('payment_date','>=',date_from),('payment_date','<=',date_to),('payment_type','=','inbound')]):
                total_amount += data.amount
            self.total_paid_invoice = total_amount
        else:
            date = str(self.today_date)
            for data in self.env['account.payment'].search([('currency_id.name','=','USD'),('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','inbound')]):
                total_amount += data.amount
            self.total_paid_invoice = total_amount


    @api.one
    def _total_expense_amount(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['account.payment'].search([('currency_id.name','=','USD'),('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','outbound')]):
                total_amount += data.amount
            self.total_expense_invoice = total_amount
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['account.payment'].search([('currency_id.name','=','USD'),('payment_date','>=',date_from),('payment_date','<=',date_to),('payment_type','=','outbound')]):
                total_amount += data.amount
            self.total_expense_invoice = total_amount
        else:
            date = str(self.today_date)
            for data in self.env['account.payment'].search([('currency_id.name','=','USD'),('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','outbound')]):
                total_amount += data.amount
            self.total_expense_invoice = total_amount


    @api.one
    def _total_invoice_amount_iqd(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['account.payment'].search([('currency_id.name','=','IQD'),('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','inbound')]):
                total_amount += data.amount
            search_id = self.env['res.currency'].search([('name','=','IQD')])
            self.total_paid_invoice_iqd = total_amount
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['account.payment'].search([('currency_id.name','=','IQD'),('payment_date','>=',date_from),('payment_date','<=',date_to),('payment_type','=','inbound')]):
                total_amount += data.amount
            self.total_paid_invoice = total_amount
        else:
            date = str(self.today_date)
        # for search_id in self.env['account.invoice'].search([('state','=','paid'),('type','=','out_invoice')]):
            for data in self.env['account.payment'].search([('currency_id.name','=','IQD'),('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','inbound')]):
                total_amount += data.amount
            search_id = self.env['res.currency'].search([('name','=','IQD')])
            self.total_paid_invoice_iqd = total_amount

    @api.one
    def _total_expense_amount_iqd(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['account.payment'].search([('currency_id.name','=','IQD'),('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','outbound')]):
                total_amount += data.amount
            search_id = self.env['res.currency'].search([('name','=','IQD')])
            self.total_expense_invoice_iqd = total_amount
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['account.payment'].search([('currency_id.name','=','IQD'),('payment_date','>=',date_from),('payment_date','<=',date_to),('payment_type','=','outbound')]):
                total_amount += data.amount
            self.total_expense_invoice_iqd = total_amount
        else:
            date = str(self.today_date)
        # for search_id in self.env['account.invoice'].search([('state','=','paid'),('type','=','out_invoice')]):
            for data in self.env['account.payment'].search([('currency_id.name','=','IQD'),('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','outbound')]):
                total_amount += data.amount
            search_id = self.env['res.currency'].search([('name','=','IQD')])
            self.total_expense_invoice_iqd = total_amount

    @api.one
    def _get_iqd_symbol(self):
        search_id = self.env['res.currency'].search([('name','=','IQD')])
        self.char_currency = search_id.symbol

    @api.one
    def _get_active_user(self):
        active_user_list = []
        for data in self.env['res.user'].search([('active','=',True)]):
            active_user_list.append(data.id)
        self.active_use_id = [(6,0, active_user_list)]

    @api.model
    def _default_date_from(self):
        date_from = False
        user = self.env.user
        datetime_from = False
        r = 'week'
        if r == 'week':
            if user.company_id.timesheet_week_start:
                if self._context.get('current_week'):
                    datetime_from = (datetime.today() + relativedelta(
                        weekday=int(user.company_id.timesheet_week_start),
                        days=-6))
                elif self._context.get('last_week'):
                    datetime_from = (datetime.today() + relativedelta(
                        weekday=int(user.company_id.timesheet_week_start),
                        days=-12))
                date_from = fields.Date.to_string(datetime_from)
        self.date_from = date_from

    @api.model
    def _default_date_to(self):
        date_to = False
        user = self.env.user
        datetime_to = False
        r = 'week'
        week_end = (int(user.company_id.timesheet_week_start) + 6) % 7
        if r == 'week':
            if self._context.get('current_week'):
                datetime_to = (datetime.today() + relativedelta(
                weekday=week_end))
            elif self._context.get('last_week'):
                datetime_to = (datetime.today() + relativedelta(
                weekday=week_end,days=-6))
            date_to = fields.Date.to_string(datetime_to)
        self.date_to = date_to

    @api.multi
    def confirm_record(self):
        serach_id = self.env['daily.sale.report'].search([('today_date','=', self.today_date)])
        if serach_id:
            raise ValidationError(_('Today Record is Already Saved'))
        else:
            self.env['daily.sale.report'].create({  'total_qty' : self.total_qty,
                                                    'total_proit' : self.total_proit,
                                                    'total_sale_order_iqd' : self.total_sale_order_iqd,
                                                    'total_sale_order' : self.total_sale_order,
                                                    'today_date' : self.today_date,
                                                    'total_paid_invoice' : self.total_paid_invoice,
                                                    'total_paid_invoice_iqd' : self.total_paid_invoice_iqd,
                                                    'total_sale' : self.total_sale,
                                                    'total_invoices' : self.total_invoices,
                                                    'total_expense' : self.total_expense,
                                                    'total_expense_invoice' : self.total_expense_invoice,
                                                    'total_expense_invoice_iqd' : self.total_expense_invoice_iqd,
                                                    'name' : self.name,
                                                    'active' : self.active,
                                                    'currency_id' : self.currency_id.id,
                                                })


    date_from = fields.Date(compute="_default_date_from")
    date_to = fields.Date(compute="_default_date_to")
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
    total_expense = fields.Integer(compute="_total_expense")
    total_expense_invoice = fields.Integer(compute="_total_expense_amount")
    total_expense_invoice_iqd = fields.Integer(compute="_total_expense_amount_iqd")
    name = fields.Char('Sales Team', required=True, translate=True)
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the sales team without removing it.")
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    color = fields.Integer(string='Color Index', help="The color of the team")
    currency_id = fields.Many2one('res.currency', string='Currency',
        default=_default_currency, track_visibility='always')
    # active_use_id = fields.Many2many('res.user','sale_dashbor_rel','dashboard_id','user_id')#,compute="_get_active_user"


    @api.multi
    def sale_order(self):
        total_amount = 0
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            search_id = self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
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

        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            search_id = self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date_from + ' 00:00:00'),
                                                      ('date_order','<=',date_to + ' 23:59:59')])

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
            search_id = self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
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
        list_id = []
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                      ('date_order','<=',date + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    list_id.append(line.id)

        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in  self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date_from + ' 00:00:00'),
                                                  ('date_order','<=',date_to + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    list_id.append(line.id)
        else:
            date = str(self.today_date)
            for data in self.env['sale.order'].search([('state','in',['done','sale']),('date_order','>=',date + ' 00:00:00'),
                                                      ('date_order','<=',date + ' 23:59:59')]):
                for line in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                    list_id.append(line.id)

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
    def sales_invoice(self):
        list_id = []
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        views = [(self.env.ref('ESCO_dashboard.view_account_payment_custom_tree').id, 'tree'), (self.env.ref('account.view_account_payment_form').id, 'form')]
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','inbound')]):
                # list_id.append(data.reconciled_invoice_ids.id)
                list_id.append(data.id)
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['account.payment'].search([('payment_date','>=',date_from),('payment_date','<=',date_to),('payment_type','=','inbound')]):
                list_id.append(data.id)
        else:
            date = str(self.today_date)
            for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','inbound')]):
                # list_id.append(data.reconciled_invoice_ids.id)
                list_id.append(data.id)
        return {
            'name': _('Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'views': views,
            'context' : "{'search_default_write_uid': 1,'search_default_currency': 1}",
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', list_id)],
        }        # search_id = self.env['account.invoice'].search([('state','=','paid'),('type','=','out_invoice'),('write_date','>=',date + ' 00:00:00'),
            #                                           ('write_date','<=',date + ' 23:59:59')])
            # return {
            #     'name': _('Sales Invoices'),
            #     'view_type': 'form',
            #     'view_mode': 'tree,form',
            #     'res_model': 'account.invoice',
            #     'view_id': False,
            #     'type': 'ir.actions.act_window',
            #     'domain': [('id', 'in', search_id.ids)],

    @api.multi
    def purchase_expenses(self):
        list_id = []
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        views = [(self.env.ref('ESCO_dashboard.view_account_payment_custom_tree').id, 'tree'), (self.env.ref('account.view_account_payment_form').id, 'form')]
        if self._context.get('yeterday'):
            date = str(yesterday.date())
            for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','outbound')]):
                # list_id.append(data.reconciled_invoice_ids.id)
                list_id.append(data.id)      
        elif self._context.get('current_week') or self._context.get('last_week'):
            date_from = str(self.date_from)
            date_to = str(self.date_to)
            for data in self.env['account.payment'].search([('payment_date','>=',date_from),('payment_date','<=',date_to),('payment_type','=','outbound')]):
                list_id.append(data.id)
        else:
            date = str(self.today_date)
            for data in self.env['account.payment'].search([('payment_date','>=',date),('payment_date','<=',date),('payment_type','=','outbound')]):
                # list_id.append(data.reconciled_invoice_ids.id)
                list_id.append(data.id)
        return {
            'name': _('Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'views': views,
            'context' : "{'search_default_write_uid': 1,'search_default_currency': 1}",
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', list_id)],
        }               # }



class SalesPersonTarget(models.Model):
    _name = 'daily.sale.report'
    _description = 'Daily Sale Report'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    total_qty = fields.Integer(string="Total Qty")
    total_proit = fields.Integer(string="Total Profit")
    total_sale_order_iqd = fields.Integer(string="Total Sale IQD")
    total_sale_order = fields.Integer(string="Total Sale USD")
    today_date = fields.Date('Order Date')
    total_paid_invoice = fields.Integer(string="Total Paid InvoiceI")
    total_paid_invoice_iqd = fields.Integer(string="Total InvoiceI IQD")
    total_sale = fields.Integer(string="Total Sale")
    total_invoices = fields.Integer(string="Total Invoices")
    total_expense = fields.Integer(string="Total Expense")
    total_expense_invoice = fields.Integer(string="Total Expense Invoice")
    total_expense_invoice_iqd = fields.Integer(string="Total Expense Invoice IQD")
    name = fields.Char(string="Name")
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the sales team without removing it.")
    currency_id = fields.Many2one('res.currency', string='Currency',default=_default_currency, track_visibility='always')