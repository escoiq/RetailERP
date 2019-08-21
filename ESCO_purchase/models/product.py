# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

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
    
    
    
