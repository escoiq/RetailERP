# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class SaleCustomReport(models.Model):
    _name = "sale.custom.report"
    _rec_name = "sequance"
    _description = "Sale Custom Report"

    @api.one 
    def _get_profit_val(self):
        self.profit_val = self.real_price - self.cost

    @api.one
    def _get_profit_per(self):
        if self.cost > 1:
            self.profit_percentage = ((self.profit_val / self.cost) * 100)
        else:
            self.profit_percentage = 0

    sequance = fields.Char(string="Sequance", default="NEW")
    sale_order_id = fields.Many2one('sale.order')
    sale_order_date = fields.Datetime(string="Order Date",related="sale_order_id.confirmation_date",store=True)
    date_order = fields.Datetime(string="Date Order",
        related="sale_order_id.date_order",store=True)
    sale_order_name = fields.Char(string="Sale Order Name",
        related="sale_order_id.name")
    product_id = fields.Many2one('product.product',string="Product Name")
    categ_id = fields.Many2one('product.category',
        related="product_id.categ_id",store=True)
    barcode = fields.Char(string="Barcode",
        related="product_id.barcode")
    qty = fields.Integer(string="Qty")
    std_price = fields.Float(string="Std. Price",
        related="product_id.list_price")
    real_price = fields.Float(string="Real S. Price")
    discount_percentage = fields.Float(string="Discount %")
    discount_value = fields.Float(string="Discount Value")
    cost = fields.Float(
        related="product_id.standard_price")
    profit_val = fields.Float(string="Profit Value",compute="_get_profit_val")
    profit_percentage = fields.Float(string="Profit %",compute="_get_profit_per")
    stock_balance = fields.Float(string="Stock Balance",
        related="product_id.qty_available")

    @api.model
    def create(self, vals):
        vals['sequance'] = self.env['ir.sequence'].next_by_code('sale.custom.report') or '/'
        return super(SaleCustomReport, self).create(vals)

    @api.model
    def _create_code(self):
        """Create Sale Report From Sale Order Line"""
        already_sale = [data.sale_order_id.id for data in self.search([])]
        for order in self.env['sale.order'].search([('id','not in',already_sale)]):
            for order_line in order.order_line:
                if order_line.price_subtotal > 1:
                    current_price = (order_line.price_subtotal / order_line.product_uom_qty)
                else:
                    current_price = order_line.product_id.list_price
                dicsount_rate = ((order_line.price_unit * order_line.discount) / 100)
                create_id = self.env['sale.custom.report'].create({                        
                            'sale_order_id' :order.id, 
                            'product_id' : order_line.product_id.id,
                            'qty' : order_line.product_uom_qty,
                            'real_price' : current_price,
                            'discount_percentage' : order_line.discount,
                            'discount_value' : dicsount_rate
                            })