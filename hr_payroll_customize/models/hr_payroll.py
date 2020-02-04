from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Waiting for finance'),
        ('confirm', 'Confirm'),
        ('close', 'Close'),


    ])

    def check_slip_ids(self):
        if not self.slip_ids:
            raise UserError("Payslips are empty!")

    @api.multi
    def compute_batch(self):
        for rec in self:
            for payslip in rec.slip_ids:
                payslip.compute_sheet()

    @api.multi
    def action_submit_batch(self):
        self.check_slip_ids()
        for rec in self:
            for payslip in rec.slip_ids:
                payslip.state = 'verify'
            rec.state = 'submit'

    @api.multi
    def action_confirm_batch(self):
        for rec in self:
            rec.state = "confirm"

    @api.multi
    def action_close_batch(self):
        for rec in self:
            for payslip in rec.slip_ids:
                payslip.action_payslip_done()
            rec.state = 'close'

    @api.multi
    def unlink(self):
        for run in self:
            if run.state not in ['draft']:
                raise UserError(_('You cannot delete a payslip which is not draft'))
        return super(HrPayslipRun, self).unlink()

    def getPivot(self):
       lines = self.env['hr.payslip.line'].search([('slip_id.payslip_run_id','=',self.id)])
       return {

       }
class hr_payslip_line(models.Model):
    _inherit="hr.payslip.line"

    employee_id=fields.Many2one(related="slip_id.employee_id")