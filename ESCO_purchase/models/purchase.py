# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
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
            print ("attribute_str>>>>>>>>.",attribute_str)
                
            if self.product_id.barcode:
                self.name += ' - ' + self.product_id.barcode

            if self.product_id.product_brand_id:
                self.name += ' - ' + self.product_id.product_brand_id.name
            
            if self.product_id.categ_id:
                self.name += ' - ' + self.product_id.categ_id.name
        return res