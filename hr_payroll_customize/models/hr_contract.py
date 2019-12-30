#-*- coding:utf-8 -*-
from odoo import fields , api, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
import time
from odoo.tools import float_compare, float_is_zero
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import dateutil.parser


_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # full_wage = fields.Monetary('Full Wage', digits=(16, 2), required=True, track_visibility="onchange",
    #                        help="=Wage with Incentive")
    #
    # undertime_rate = fields.Monetary('Under-time Rate', digits=(16, 2), required=True,
    #                                  track_visibility="onchange", default=0)
    #
    # overtime_rate = fields.Monetary('Over-time Rate', digits=(16, 2), required=True,
    #                                  track_visibility="onchange", default=0)
    #
    basic = fields.Integer()

