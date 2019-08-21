# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AppThemeConfigSettings(models.TransientModel):
    _inherit = 'sale.retail.report.config.settings'

    kanaban_menu = fields.Boolean('Hide or Show Kanaban Report',
                                   help="Easily Hide and Show Kanaban Report")
 

    @api.model
    def get_values(self):
        res = super(AppThemeConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter']
        kanaban_menu = True if ir_config.sudo().get_param('kanaban_menu') == "True" else False
        res.update(
            kanaban_menu=kanaban_menu)
        return res

    @api.multi
    def set_values(self):
        super(AppThemeConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter']
        self.ensure_one()
        ir_config.set_param("kanaban_menu", self.kanaban_menu or "False")
        if self.kanaban_menu:
            group_e = self.env.ref('ESCO_dashboard.group_invoice_kanban', True)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(4, data.id)]})
        else:
            group_e = self.env.ref('ESCO_dashboard.group_invoice_kanban', False)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(3, data.id)]})
        return True
