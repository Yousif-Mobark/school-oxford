# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

class HrEmployee(models.Model):
    _name = 'hr.employee.customize'

    name = fields.Char(string="Employee Name", required=1)
    department_id = fields.Many2one("hr.department")
    job_id = fields.Many2one("hr.job")
    user_id = fields.Many2one("res.users", "Related User")
    wage = fields.Float("Wage", required=1)
    basic = fields.Integer()
    salary_structure = fields.Many2one("hr.payroll.structure", required=1)
    gender = fields.Selection([('male', "Male"), ('female', "Female")])
    manager_id = fields.Many2one("hr.employee", "Manager")
    is_manager = fields.Boolean("Is Manager")
    date = fields.Date("Date")
    contract_type_id = fields.Many2one("hr.contract.type", string="Contract Type", required=1)
    working_schedule = fields.Many2one("resource.calendar", string="Working Schedule", required=1)
    employee_id = fields.Many2one("hr.employee")
    contract_id = fields.Many2one("hr.contract")
    state = fields.Selection([('draft', "Draft"), ('done', "Done")], default='draft')

    @api.multi
    def action_done(self):
        if self.state == 'draft':
            employee_id = self.create_employee()
            contract_id = self.create_contract(employee_id)
            self.employee_id = employee_id.id
            self.contract_id = contract_id.id
            self.state = 'done'

    @api.model
    def create_employee(self):
        emp_obj = self.env["hr.employee"]
        for rec in self:
            vals = {
                'user_id': rec.user_id.id,
                'name': rec.name,
                'department_id': rec.department_id.id,
                'job_id': rec.job_id.id,
                'parent_id': rec.manager_id.id,
                'manager': rec.is_manager,
                'gender': rec.gender,
            }

            employee_id = emp_obj.create(vals)
            if employee_id:
                # Employee name effected by user
                employee_id.write({'name': rec.name})
                return employee_id
        return False

    @api.model
    def create_contract(self, employee_id):
        contract_obj = self.env["hr.contract"]
        for rec in self:
            vals = {
                'name': employee_id.name,
                'employee_id': employee_id.id,
                'department_id': employee_id.department_id.id,
                'job_id': employee_id.job_id.id,
                'basic':rec.basic,
                'wage': rec.wage,
                'type_id': rec.contract_type_id.id,
                'struct_id': rec.salary_structure.id,
                'resource_calender_id': rec.working_schedule.id,
                'date_start': rec.date,
                'state': 'open'
            }
            return contract_obj.create(vals)

    @api.multi
    def action_open_employee(self):
        self.ensure_one()
        action = self.env.ref('hr.open_view_employee_list_my').read()[0]
        action['domain'] = [('id', '=', self.employee_id.id)]
        return action

    @api.multi
    def action_open_contract(self):
        self.ensure_one()
        action = self.env.ref('hr_contract.action_hr_contract').read()[0]
        action['domain'] = [('id', '=', self.contract_id.id)]
        return action

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(
                    _('You cannot delete Form which is not is draft.'))
        return super(HrEmployee, self).unlink()

