# -*- coding: utf-8 -*-
from odoo import fields, models

_WEEKDAYS = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday')
]


class ResCompany(models.Model):
    _inherit = 'res.company'

    timesheet_week_start = fields.Selection(
        _WEEKDAYS, string='Week start day', default='0')
