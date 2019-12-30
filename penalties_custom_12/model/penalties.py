from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import except_orm, Warning, UserError


class irregularities(models.Model):
    _name = 'hr.penalties'
    _inherit = 'mail.thread'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    penalty = fields.One2many('penal.penal', 'hr_penalty_id', string='Penalties Lines')

    def toggle_active(self):
        res = super(irregularities, self).toggle_active()
        return res


class Penalties(models.Model):
    _name = 'penal.penal'

    name = fields.Char(string='Name', required=True)
    penalties_no = fields.Integer(string='Sequence', required=True, default=1)
    type = fields.Selection([('deduction', 'Deduction'),
                             ("worrying", "Worrying")], string='Penalties type', required=True)
    duration = fields.Integer(string='Duration in Days', default=180, required=True)
    hr_penalty_id = fields.Many2one('hr.penalties', string='Hr Penalty', required=True)
    deduction = fields.Many2one('deduction.type', string='Deduction')


class EmployeePenalties(models.Model):
    _name = 'hr.employee.penalties'
    _inherit = 'mail.thread'
    _rec_name = "employee"

    state = fields.Selection(
        [('draft', 'Draft'), ("confirm", "Confirm"), ('hr_manager', 'Hr Manager'), ('done', 'Done')],
        default='draft', string='State')
    employee = fields.Many2one('hr.employee', string="Employee", required=True, track_visibility='onchange')
    dep = fields.Many2one('hr.department', string='Department', required=True, track_visibility='onchange')
    date = fields.Date(string="Date", default=date.today(), required=True, track_visibility='onchange')
    hr_penalty_id = fields.Many2one('hr.penalties', string='Hr Penalty', required=True, track_visibility='onchange')
    current_penalty = fields.Many2one('penal.penal', string='Current penalty', track_visibility='onchange')
    previous = fields.Many2one('penal.penal', string='Previous penalty', track_visibility='onchange')
    current_pointer = fields.Boolean(string='Pointer', track_visibility='onchange')
    deduction_type = fields.Many2one('deduction.type', string='Deduction Type', readonly=True, track_visibility='onchange')
    type = fields.Selection([('deduction', 'Deduction'), ("worrying", "Worrying")], string='Penalties type',
                            track_visibility='onchange')
    deduc_ref = fields.Many2one('deduction.deduction', string='Deduction reference', readonly=True,
                                track_visibility='onchange')
    flag = fields.Boolean(string='Flag', default=False)

    @api.onchange('employee')
    def get_employee_department(self):
        if self.employee:
            self.dep = self.employee.department_id

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(
                    _('You cannot delete Form which is not is draft.'))
        return super(EmployeePenalties, self).unlink()

    @api.multi
    def action_compute_penalties(self):
        penalty_obj = self.env['hr.employee.penalties'].search([('employee', '=', self.employee.id)])
        for p in penalty_obj:
            if p.hr_penalty_id == self.hr_penalty_id and p.current_pointer == True:
                for penalty in penalty_obj:
                    if penalty.current_pointer == True:
                        validat_date = datetime.strptime(str(penalty.date), '%Y-%m-%d').date()
                        if penalty.current_penalty.duration >= (validat_date - date.today()).days:
                            penalty.current_pointer = False
                            self.previous = penalty.current_penalty.id
                            for con_p in self.hr_penalty_id.penalty:
                                if con_p.penalties_no > self.previous.penalties_no:
                                    self.current_penalty = con_p.id
                                    self.deduction_type = con_p.deduction.id
                                    self.current_pointer = True
                                    self.flag = True
                                    return
                        else:
                            penalty.current_pointer = False
                            for pen in self.hr_penalty_id.penalty:
                                self.current_penalty = pen.id
                                self.deduction_type = pen.deduction.id
                                self.current_pointer = True
                                self.flag = True
                                return
        for pen in self.hr_penalty_id.penalty:
            self.current_penalty = pen.id
            self.current_pointer = True
            self.flag = True
            self.flag = True
            return

    @api.multi
    def action_confirm(self):
        if self.current_penalty:
            penalty_obj = self.env['hr.employee.penalties'].search([('employee', '=', self.employee.id)])
            for rec in self:
                if rec.state == 'draft':
                    rec.state = 'confirm'
                for p in penalty_obj:
                    if p.current_pointer == True:
                        p.current_pointer = False
        else:
            self.action_compute_penalties()

    @api.multi
    def action_hr_approve(self):
        for rec in self:
            rec.state = 'hr_manager'
            rec.current_pointer = False

    @api.multi
    def action_ceo_approve(self):
        for rec in self:
            if rec.state == 'hr_manager':
                if rec.current_penalty.type == 'deduction':
                    self.create_employee_deduction()
                rec.state = 'done'

    def create_employee_deduction(self):
        return
        deduction_obj = self.env['deduction.deduction']
        dic = {
            'name': 'Deduction',
            'employee': self.employee.id,
            'data': self.date,
            'deduction_type': self.deduction_type.id,
            'fix_formula': 'fix',
            'description': 'Employee Deduction',
        }
        ref = deduction_obj.create(dic)
        self.write({'deduc_ref': ref.id})
