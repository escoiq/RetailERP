# -*- coding: utf-8 -*-
# © 2009 NetAndCo (<http://www.netandco.net>).
# © 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>
# © 2014 prisnet.ch Seraphine Lantible <s.lantible@gmail.com>
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2018 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _order = 'name'

    name = fields.Char('Brand Name', required=True)
    description = fields.Text('Description', translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Select a partner for this brand if any.',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File')
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_get_products_count',
    )

    @api.multi
    @api.depends('product_ids')
    def _get_products_count(self):
        for brand in self:
            brand.products_count = len(brand.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
    )
    brand_name = fields.Char(related='product_brand_id.name', string="Brand Name", store=True)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_name = fields.Char(related='product_brand_id.name', string="Brand Name", store=True)
    
# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#     @api.model
#     def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
#         print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.name ", name)
#         if not args:
#             args = [['brand_name', 'ilike', name]]
#         else:
#             args += [['brand_name', 'ilike', name]]
#         res = super(ProductProduct, self)._name_search( name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
#
#         print ("res-----------args--",args)
#         print ("res-------------",res)
#         return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_brand_id = fields.Many2one(
        related='product_id.product_brand_id',
        string='Brand',
        store=True
    )
