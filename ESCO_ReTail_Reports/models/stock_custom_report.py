# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class SaleCustomReport(models.Model):
    _name = "sale.custom.report"
    _rec_name = "sequance"
    _description = "Sale Retial Report"


    @api.one 
    def _get_profit_val(self):
        self.profit_val = self.real_price - self.cost
    @api.one
    def _get_profit_per(self):
        if self.cost > 1:
            self.profit_percentage = ((self.profit_val / self.cost) * 100)
        else:
            self.profit_percentage = 0

    @api.one
    def _get_id(self):
        self.sequance = self.id

    sequance = fields.Integer(string="Sequance",compute="_get_id")
    sale_order_id = fields.Many2one('sale.order')
    sale_order_date = fields.Datetime(string="Order Date",related="sale_order_id.confirmation_date",store=True)
    date_order = fields.Datetime(string="Date Order",related="sale_order_id.date_order",store=True)
    sale_order_name = fields.Char(string="Sale Order Name",related="sale_order_id.name")
    product_id = fields.Many2one('product.product',string="Product Name")
    categ_id = fields.Many2one('product.category',related="product_id.categ_id",store=True)
    barcode = fields.Char(related="product_id.barcode",string="Barcode")
    qty = fields.Integer(string="Qty")
    std_price = fields.Float(related="product_id.list_price",string="Std. Price")
    real_price = fields.Float(string="Real S. Price")
    discount_percentage = fields.Float(string="Discount %")
    discount_value = fields.Float(string="Discount Value")
    cost = fields.Float(related="product_id.standard_price")
    profit_val = fields.Float(string="Profit Value",compute="_get_profit_val")
    profit_percentage = fields.Float(string="Profit %",compute="_get_profit_per")
    stock_balance = fields.Float(string="Stock Balance",related="product_id.qty_available")

    @api.model
    def _create_code(self):
        already_sale = []
        for data in self.env['sale.custom.report'].search([]):
            already_sale.append(data.sale_order_id.id)
        for data in self.env['sale.order'].search([('id','not in',already_sale)]):
            for inner_data in self.env['sale.order.line'].search([('order_id','=',data.id)]):
                if inner_data.price_subtotal > 1:
                    current_price = (inner_data.price_subtotal / inner_data.product_uom_qty)
                else:
                    current_price = inner_data.product_id.list_price
                dicsount_rate = ((inner_data.price_unit * inner_data.discount) / 100)
                create_id = self.env['sale.custom.report'].create({
                                                                 
                                                                  'sale_order_id' :data.id, 
                                                                  'product_id' : inner_data.product_id.id,
                                                                  'qty' : inner_data.product_uom_qty,
                                                                  'real_price' : current_price,
                                                                  'discount_percentage' : inner_data.discount,
                                                                  'discount_value' : dicsount_rate
                                                                })
                next_seq = create_id.sequance + 1
                create_id.write({'sequance' : next_seq})