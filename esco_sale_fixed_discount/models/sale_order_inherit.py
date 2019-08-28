# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def name_get(self):
        # TDE: this could be cleaned a bit I think
        is_on_sale = 'show_qty' in self.env.context and self.env.context.get('show_qty')
        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            ir_config = self.env['ir.config_parameter']
            show_qty_order_line = True if ir_config.sudo().get_param('show_qty_order_line') == "True" else False
            qty = d.get('qty_avialble')
            if code:
                if is_on_sale and show_qty_order_line:
                    name = '[qty %s] [%s] %s' % (qty,code,name)
                else: 
                    name = '[%s] %s' % (code,name)
            elif is_on_sale and show_qty_order_line:
                name = '[qty %s] %s' % (qty,name)
            else:
                name = '%s' % (name)

            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []

        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'default_code', 'product_tmpl_id', 'attribute_value_ids'], load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            # display only the attributes with multiple possible values on the template
            variable_attributes = product.attribute_value_ids.filtered(lambda v: len(v.attribute_id.value_ids) > 1).mapped('attribute_id')
            variant = product.attribute_value_ids._variant_name(variable_attributes)

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              'qty_avialble' : product.qty_available,
                              }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          'qty_avialble' : product.qty_available,
                          }
                result.append(_name_get(mydict))
        return result

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total','order_line.product_uom_qty','order_line.price_unit')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = discount_amount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                discount_amount += ((line.price_unit * line.product_uom_qty) - line.price_subtotal)
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'total_discount' : discount_amount,
            })

    total_discount = fields.Float('Total discount',compute='_amount_all')

    @api.multi
    def _prepare_invoice(self,):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'total_discount': self.total_discount
        })
        return invoice_vals

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount_total for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        self.total_discount = (sum(line.price_unit * line.quantity for line in self.invoice_line_ids) - sum(line.price_subtotal for line in self.invoice_line_ids))
        self.subtotal_without_discount = sum(line.price_unit * line.quantity for line in self.invoice_line_ids)
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
            amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    total_discount = fields.Float('Total discount',compute='_compute_amount')
    subtotal_without_discount = fields.Float('Subtotal Without discount',compute='_compute_amount')

class SaleOrderline(models.Model):
    _inherit = "sale.order.line"

    discount_amount = fields.Float(string='Discount Amount', digits=dp.get_precision('Product Price'), default=0.0)
    cost_price = fields.Float(related="product_id.standard_price",string="Cost") 

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','discount_amount')
    def _compute_amount(self):
        """ Compute the amounts of the SO line."""
        for line in self:
            if line.discount:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            elif line.discount_amount:
                price = line.price_unit - line.discount_amount
            else:
                price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)    
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.multi
    def _prepare_invoice_line(self,qty):
        invoice_vals = super(SaleOrderline, self)._prepare_invoice_line(qty)
        invoice_vals.update({
            'discount_amount': self.discount_amount
        })
        return invoice_vals


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount_amount = fields.Float(string='Discount Amount', digits=dp.get_precision('Product Price'), default=0.0)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date','discount_amount')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        if self.discount:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        elif self.discount_amount:
            price = self.price_unit - self.discount_amount
        else:
            price = self.price_unit            
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(price_subtotal_signed, self.invoice_id.company_id.currency_id, self.company_id or self.env.user.company_id, date or fields.Date.today())
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] 
