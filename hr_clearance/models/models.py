# -*- coding: utf-8 -*-
from pytz import timezone, UTC
from odoo import api, fields, models
from odoo.exceptions import UserError


class HrClearance(models.Model):
    _name = "hr.clearance"
    _inherit = ["mail.thread"]
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    emp_department_id = fields.Many2one('hr.department', string='Department', track_visibility='onchange')
    job_id = fields.Many2one('hr.job', 'Job Position')
    h_date = fields.Date(string="Hiring Date")
    reason_of_clearance = fields.Selection([
        ('end_of_contract', 'End of contract'),
        ('End_Of_trail_period', 'End Of trail period'),
        ('resignation', 'Resignation'),
        ('offal_dismissal', 'Offal Dismissal'),
    ], string='Reason Of Clearance', required=True, default='end_of_contract')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        )

    @api.onchange('employee_id')
    def get_employee_department(self):
        if self.employee_id:
            self.emp_department_id = self.employee_id.department_id
            self.job_id = self.employee_id.job_id

    def draft_to_submitted(self):
        self.state = 'submitted'
    
    def submitted_to_confirmed(self):
        self.state = 'confirmed'

    def confirmed_to_done(self):
        self.state = 'done'
    
    def got_to_draft(self):

        if self.state != "done":
            self.state = "draft"

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(
                    _('You cannot delete Form which is not is draft.'))
        return super(HrClearance, self).unlink()
