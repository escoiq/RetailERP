# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AppThemeConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'sale.retail.config'
    _description = "Show Hide Sale Retail Report"

    hide_show_menu = fields.Boolean('Hide or Show Retail Report',
                                   help="Easily Hide and Show Retail Sale Repoot")


    @api.model
    def get_values(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        hide_show_menu = True if ir_config.get_param('hide_show_menu') == "True" else False
        return dict(
            hide_show_menu=hide_show_menu,
        )

    @api.multi
    def set_values(self):
        ir_config = self.env['ir.config_parameter']
        self.ensure_one()
        ir_config.set_param("hide_show_menu", self.hide_show_menu or "False")
        if self.hide_show_menu:
            group_e = self.env.ref('esco_retail_reports.group_sale_report', True)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(4, data.id)]})
        else:
            group_e = self.env.ref('esco_retail_reports.group_sale_report', False)
            for data in self.env['res.users'].search([]):
                group_e.write({'users': [(3, data.id)]})
        return True
