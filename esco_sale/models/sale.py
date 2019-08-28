# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def action_confirm(self):
        if self.env.user.company_id.force_restrict_sale_stock:
            for order in self:
                for line in order.order_line:
                    if line.product_id and line.product_id.type == 'product':
                        draft_qty = sum([ x.product_uom_qty for x in self.env['sale.order.line'].search([
                                                                        ('product_id','=',line.product_id.id),
                                                                        ('state','in', ['draft','sent']),
                                                                        ('id','!=',line.id) ]) ])
                        actual_available_qty = line.product_id.qty_available - draft_qty
                        if not actual_available_qty >= line.product_uom_qty:
                            raise UserError(_(
                                'Quantity on hand for the product : %s is not sufficient !'
                            ) % (line.product_id.name) )
        return super(sale_order, self).action_confirm()
    
    @api.multi
    def cancel_order_older_then_3hour(self):
        back_datetime = (datetime.now() - timedelta(hours=3)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        order = self.search([('create_date','<',back_datetime),('state','=','draft')])
        if order:
            order.action_cancel()
            
class sale_order_line(models.Model):
    _inherit = "sale.order.line"            
            
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(sale_order_line, self).product_id_change()
        if self.product_id:
            self.name = ''
            if self.product_id.default_code:
                self.name += '[' + self.product_id.default_code + ']' + self.product_id.name
            else:
                self.name += self.product_id.name

            attribute_str = ''
            for att_value in self.product_id.attribute_value_ids:
                if attribute_str:
                    attribute_str += ', '
                attribute_str += '('+att_value.attribute_id.name + ':' + att_value.name +')'
                
            if attribute_str:
                self.name += ' - ' + attribute_str
                
            if self.product_id.barcode:
                self.name += ' - ' + self.product_id.barcode

            if self.product_id.product_brand_id:
                self.name += ' - ' + self.product_id.product_brand_id.name
            
            if self.product_id.categ_id:
                self.name += ' - ' + self.product_id.categ_id.name
        return res