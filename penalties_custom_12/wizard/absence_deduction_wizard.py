# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class AbsenceDeductionWizard(models.TransientModel):
    _name = 'absence.deduction.wizard'
    _description = "Absence deduction"

    employees_selection = fields.Selection([('all', 'All Employees'), ('selected', 'Selected Employees')],
                                           "Selected Employees", default='all')
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    deduction_type_id = fields.Many2one('deduction.type', "Deduction Type", required=1)
    date_from = fields.Date("Date From", required=1)
    date_to = fields.Date("Date To", required=1)

    @api.constrains('date_from', 'date_to')
    def check_from_lt_to(self):
        if self.date_from and self.date_to:
            if self.date_from >= self.date_to:
                raise ValueError(_("Date from must be less than date to"))

    @api.multi
    def calculate_deductions(self):
        # Get working days between given dates
        working_days = []
        delta = self.date_to - self.date_from
        for i in range(delta.days + 1):
            day = self.date_from + timedelta(days=i)
            if day.weekday() in [6, 0, 1, 2, 3]:
                working_days.append(day)

        # Calculate Deductions
        if self.employees_selection == 'all':
            employees = self.env['hr.employee'].search([])
            for employee in employees:
                attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '<=', self.date_to),
                    ('check_in', '>=', self.date_from)
                ])
                contracts = self.env['hr.contract'].search([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'open')
                ])
                contract = contracts[0] if len(contracts) > 0 else False
                for day in working_days:
                    if contract and not attendances.filtered(lambda attendance: attendance.check_in.date() == day):
                        exists = self.env['deduction.deduction'].search([
                            ('name', '=', 'ABSENT ON {} DEDUCTION '.format(day)),
                            ('employee', '=', employee.id)
                        ])
                        if exists:
                            self.env['deduction.deduction'].create({
                                'employee': employee.id,
                                'deduction_type': self.deduction_type_id.id,
                                'description': 'ABSENCE DEDUCTION',
                                'name': 'ABSENT ON {} DEDUCTION '.format(day),
                                'fix_formula': 'fix',
                                'amount': contract.wage / 30,
                            })

        else:
            employees = self.employee_ids
            for employee in employees:
                attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '<=', self.date_to),
                    ('check_in', '>=', self.date_from)
                ])
                contracts = self.env['hr.contract'].search([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'open')
                ])
                contract = contracts[0] if len(contracts) > 0 else False
                for day in working_days:
                    if contract and not attendances.filtered(lambda attendance: attendance.check_in.date() == day):
                        exists = self.env['deduction.deduction'].search([
                            ('name', '=', 'ABSENT ON {} DEDUCTION '.format(day)),
                            ('employee', '=', employee.id)
                        ])
                        if not exists:
                            self.env['deduction.deduction'].create({
                                'employee': employee.id,
                                'deduction_type': self.deduction_type_id.id,
                                'description': 'ABSENCE DEDUCTION',
                                'name': 'ABSENT ON {} DEDUCTION '.format(day),
                                'fix_formula': 'fix',
                                'amount': contract.wage / 30,
                            })
