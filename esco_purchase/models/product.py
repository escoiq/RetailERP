# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class product_template(models.Model):
    _inherit = "product.template"

    name = fields.Char('Name', index=True, required=True, translate=False)

    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.default_code = template.product_variant_ids.default_code
        for template in (self - unique_variants):
            template.default_code = ''

    @api.one
    def _set_default_code(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.default_code = self.default_code

    

    default_code = fields.Char(
        'Part No.', compute='_compute_default_code',
        inverse='_set_default_code', store=True)
    
class product_product(models.Model):
    _inherit = "product.product"
    
    default_code = fields.Char('Part No.', index=True)
    
    def get_name_for_line(self):
        """Compute name for product to be used in Invoice line"""
        name = ''
        if self.default_code:
            name += '[' + self.default_code + ']' + self.name
        else:
            name += self.name

        attribute_str = ''
        for att_value in self.attribute_value_ids:
            if attribute_str:
                attribute_str += ', '
            attribute_str += '('+att_value.attribute_id.name + ':' + att_value.name +')'
            
        if attribute_str:
            name += ' - ' + attribute_str
            
        if self.barcode:
            name += ' - ' + self.barcode

        if self.product_brand_id:
            name += ' - ' + self.product_brand_id.name

        if self.categ_id:
            name += ' - ' + self.categ_id.name
        return name
