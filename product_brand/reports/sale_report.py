# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
    )

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        return super(SaleReport, self)._query(with_clause='', fields={'field':', t.product_brand_id'}, groupby=', t.product_brand_id', from_clause='')


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    product_brand_id = fields.Many2one('product.brand',string='Brand')

    def _select(self):
        return super(PurchaseReport, self)._select() + ", t.product_brand_id"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", t.product_brand_id"

