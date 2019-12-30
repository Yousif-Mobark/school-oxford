#-*- coding:utf-8 -*-
from odoo import fields , api, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import logging


_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    leave_days = fields.Integer('Leave Days', default=0, required=True, track_visibility="onchange",
                           help="=Number of annual leave days")


#####################################################################


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    start_date = fields.Date('Start Date',  track_visibility="onchange",
                           help="=Number of annual leave days")

