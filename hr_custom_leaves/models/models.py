# -*- coding: utf-8 -*-

import logging
import math

from collections import namedtuple

from datetime import datetime, time
from pytz import timezone, UTC

from odoo import api, fields, models
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

# Used to agglomerate the attendances in order to find the hour_from and hour_to
# See _onchange_request_parameters
DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period')


############################# 
######## Hr leaves     ######
#############################
class customHolidaysType(models.Model):
    _inherit = "hr.leave"

    employee_rep_id = fields.Many2one('hr.employee', string="Employee Replacement", domain = "[('id','!=',employee_id)]")

    number_of_days = fields.Float(
        'Duration (Days)', copy=False, readonly=True, track_visibility='onchange',
        states={'draft': [('readonly', False)],'submit': [('readonly', False)],'supervisor': [('readonly', False)],'gm_approval': [('readonly', False)], 'confirm': [('readonly', False)]},
        help='Number of days of the leave request according to your working schedule.')


    state = fields.Selection([
        ('submit', 'Draft'),   
        ('supervisor', 'Supervisor approval'),
        ('gm_approval', 'General Manager Approval'),
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='submit',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'General Manager Approval', when leave request is approved by the general manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")



    @api.multi
    def draft_supervisor(self):
        self.write({'state': 'supervisor'})

    @api.one
    def supervisor_approval(self):
        
        if self.holiday_status_id.gm_approval:
            self.state = 'gm_approval'
        else:
            self.state = 'confirm'

    @api.one
    def gm_approval(self):
        self.state = 'draft'



#############################
######## Hr leave type ######
#############################
class customHolidaysType(models.Model):
    _inherit = "hr.leave.type"

    # TODO: Add the general manager approval
    gm_approval = fields.Boolean(string='Apply General Manager Approval',
        help="When selected, the Allocation/Leave Requests for this type require the general manager to be approved.")

