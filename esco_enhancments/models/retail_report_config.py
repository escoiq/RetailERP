# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _


class AppThemeConfigSettings(models.TransientModel):
    _inherit = 'sale.retail.config'

    show_enhancement = fields.Boolean('Show total invoice and Amount due')
    
    @api.model
    def get_values(self):
        res = super(AppThemeConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        show_enhancement = True if ir_config.get_param('show_enhancement') == "True" else False
        res.update(
            show_enhancement=show_enhancement)
        return res

    @api.multi
    def set_values(self):
        res = super(AppThemeConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter']
        self.ensure_one()
        ir_config.set_param("show_enhancement", self.show_enhancement or "False")
        if self.show_enhancement:
            group_e = self.env.ref('esco_enhancments.group_esco_enhance', True)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(4, data.id)]})
        else:
            group_e = self.env.ref('esco_enhancments.group_esco_enhance', False)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(3, data.id)]})        
        return res