# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _


class AppThemeConfigSettings(models.TransientModel):
    _inherit = 'sale.retail.config'

    restict_account_user = fields.Boolean('Restrict Accounting Menu (Vendor Menu) to Account User')

    @api.model
    def get_values(self):
        res = super(AppThemeConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter']
        restict_account_user = True if ir_config.sudo().get_param('restict_account_user') == "True" else False
        res.update(
            restict_account_user=restict_account_user)
        return res

    @api.multi
    def set_values(self):
        super(AppThemeConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter']
        self.ensure_one()
        ir_config.set_param("restict_account_user", self.restict_account_user or "False")
        menu_id = self.env.ref('account.menu_finance_payables')
        group_list = []
        if self.restict_account_user:
            group_list.append(self.env.ref('account.group_account_manager').id)
            group_list.append(self.env.ref('base.group_erp_manager').id)
            menu_id.write({'groups_id' : [(6,0, group_list)] })
            rule_id = self.env.ref('esco_account.restict_accont_user_vendor_payment')
            rule_id.write({'active' : True})
        else:
            blank_list = []
            menu_id.write({'groups_id' : [(6,0, blank_list)] })
            rule_id = self.env.ref('esco_account.restict_accont_user_vendor_payment')
            rule_id.write({'active' : False})
        return True


