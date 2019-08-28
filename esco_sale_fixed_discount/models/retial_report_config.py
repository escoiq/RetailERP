# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _


class AppThemeConfigSettings(models.TransientModel):
    _inherit = 'sale.retail.config'

    show_qty_order_line = fields.Boolean('Show Qty on Dropdown')
    discount_amount = fields.Boolean('Hide or Show Discount Amount',
                                   help="Easily Hide and Show Discount amount in sale order")
 
    @api.model
    def get_values(self):
        res = super(AppThemeConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter']
        discount_amount = True if ir_config.sudo().get_param('discount_amount') == "True" else False
        show_qty_order_line = True if ir_config.sudo().get_param('show_qty_order_line') == "True" else False
        res.update(
            discount_amount=discount_amount,
            show_qty_order_line=show_qty_order_line)
        return res

    @api.multi
    def set_values(self):
        super(AppThemeConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter']
        self.ensure_one()
        ir_config.set_param("discount_amount", self.discount_amount or "False")
        ir_config.set_param("show_qty_order_line", self.show_qty_order_line or "False")
        if self.discount_amount:
            group_e = self.env.ref('esco_sale_fixed_discount.group_discount_fix', True)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(4, data.id)]})
        else:
            group_e = self.env.ref('esco_sale_fixed_discount.group_discount_fix', False)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(3, data.id)]})
        if self.show_qty_order_line:
            group_e = self.env.ref('esco_sale_fixed_discount.group_show_qty', True)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(4, data.id)]})
        else:
            group_e = self.env.ref('esco_sale_fixed_discount.group_show_qty', False)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(3, data.id)]})            
        return True