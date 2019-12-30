from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import except_orm, Warning, UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.tools.safe_eval import safe_eval


class Deduction(models.Model):
    _name = 'deduction.deduction'
    _inherit = 'mail.thread'

    name = fields.Char(string='Reference', required=True)
    deduction_no = fields.Char(string='Sequence', readonly=True)
    date = fields.Date(string="Date", default=date.today())
    employee = fields.Many2one('hr.employee', string="Employee", required=True)
    deduction_type = fields.Many2one('deduction.type', string='Deduction Type', required=True)
    fix_formula = fields.Selection([('formula', 'Formula'), ("fix", "Fixed")], string='Calculation Type', required=True,
                                   default='fix')
    amount = fields.Float(string="Amount")
    description = fields.Text(string='Description', required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ("confirm", "Confirm"),
                              ('hr_manager', 'Hr'),
                              ('done', 'Done')],
                             default='draft', string='State', track_visibility='onchange')
    voucher_ref = fields.Many2one('account.voucher', string='Voucher reference', readonly=True)
    is_paid = fields.Boolean()
    formual = fields.Text(placeholder="result=(wage/30)*1")

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(
                    _('You cannot delete Form which is not is draft.'))
        return super(Deduction, self).unlink()

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.amount <= 0:
                if rec.fix_formula != 'fix':
                    raise ValidationError("Please click on calc amount button, and amount must be greater than zero")
                raise ValidationError(_("Amount Must Be Greater Than Zero"))
            if rec.state == 'draft':
                rec.state = 'confirm'
            #     if rec.deduction_type.pay_included == 'voucher':
            #         self.generate_voucher()
            # else:
            #     raise UserError("In order to confirm this deduction state must be in draft")

    @api.one
    def generate_voucher(self):
        voucher_obj = self.env['account.voucher']
        payable_account_id = self._default_payable_account_id()
        expense_account_id = self._default_expense_account_id()
        journal_id = self._default_journal_id()
        if not payable_account_id:
            raise ValidationError("Please check configuration for default voucher payable account")
        if not expense_account_id:
            raise ValidationError("Please check configuration for default voucher expense account")
        if not journal_id:
            raise ValidationError("Please check configuration for default voucher journal")

        if self.deduction_type.pay_included == 'voucher':
            employee_default_account_id = self.employee.address_home_id and self.employee.address_home_id.property_account_payable_id
            voucher_id = voucher_obj.create({
                'journal_id': journal_id.id,
                'voucher_type': 'purchase',
                'pay_now': 'pay_later',
                'state': 'draft',
                'account_id': employee_default_account_id.id or payable_account_id.id,
                'line_ids': [(0, 0, {'name': self.description or '/',
                                     'quantity': 1,
                                     'price_unit': self.amount,
                                     'account_id': expense_account_id.id})]})

            voucher_id.proforma_voucher()
            self.write({'voucher_ref': voucher_id.id})

    @api.model
    def _default_payable_account_id(self):
        account_id = self.env['ir.config_parameter'].sudo().get_param(
            'penalties_custom_12.default_voucher_payable_account_id')
        return self.env['account.account'].browse(int(account_id))

    @api.model
    def _default_expense_account_id(self):
        account_id = self.env['ir.config_parameter'].sudo().get_param(
            'penalties_custom_12.default_voucher_expense_account_id')
        return self.env['account.account'].browse(int(account_id))

    @api.model
    def _default_journal_id(self):
        journal_id = self.env['ir.config_parameter'].sudo().get_param('penalties_custom_12.default_journal_id')
        return self.env['account.journal'].browse(int(journal_id))

    @api.multi
    def action_hr_approval(self):
        for rec in self:
            if rec.state == 'confirm':
                rec.state = 'hr_manager'
            else:
                raise (_("In order to approve this deduction state must be in confirm"))

    def set_amount(self):
        for rec in self:
            amount = self.calc_amount(employee_id=rec.employee, contract=rec.employee.contract_id, rec=self).get('result', False)
            rec.amount = amount


    @api.onchange('fix_formula')
    def set_formula(self):
        if not self.formual:
            self.formual=self.deduction_type.formual

    @api.model
    def _default_calc_formula(self):
        calc_formula = self.env['ir.config_parameter'].sudo().get_param(
            'penalties_custom_12.calc_formula')
        return self.formual

    def calc_amount(self, employee_id, contract, rec):
        employee = self.env['hr.employee'].browse(employee_id)
        formula_data = self._default_calc_formula()
        if not formula_data:
            raise ValidationError("Please Check payroll Configuration. Set formula")
        localdict = {"employee_id": employee, "wage": contract.wage, "deduction": self, "contract": contract, 'result': 0}
        safe_eval(formula_data, localdict, mode='exec', nocopy=True)
        return localdict

    @api.multi
    def action_ceo_approve(self):
        for rec in self:
            if rec.state == 'hr_manager':
                rec.state = 'done'
            else:
                raise (_("In order to ceo approve this deduction state must be in hr approve"))


class BonceType(models.Model):
    _name = 'deduction.type'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)

    formual = fields.Text( )


    def toggle_active(self):
        res = super(BonceType, self).toggle_active()
        return res


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    deduction = fields.Float(string='Deduction', compute='_compute_deduction')
    deduction_line = fields.One2many('deduction.line', 'payslip', string='Deduction line', )

    @api.onchange('employee_id')
    def payslip_deduction(self):
        employee_deduction_ids = self.env['deduction.deduction'].search([('employee', '=', self.employee_id.id),
                                                                         ('is_paid', '=', False),
                                                                         ('state', '=', 'done')])
        if self.deduction_line:
            self.deduction_line.sudo().unlink()
        lines = self.deduction_line.browse()
        for deduction in employee_deduction_ids:
            if deduction.deduction_type:
                lines += lines.new({
                    'deduction_id': deduction.id,
                    'payslip': self.id,
                    'name': deduction.name,
                    'amount': deduction.amount,
                    'description': deduction.description,
                    'date': deduction.date,
                })
        self.deduction_line = lines

    @api.multi
    def action_payslip_done(self):
        for rec in self:
            for line in rec.deduction_line:
                line.deduction_id.is_paid = True
        return super(Payslip, self).action_payslip_done()

    @api.depends('deduction_line')
    def _compute_deduction(self):
        for rec in self:
            for lin in rec.deduction_line:
                rec.deduction += lin.amount


class deductionLine(models.Model):
    _name = 'deduction.line'

    deduction_id = fields.Many2one("deduction.deduction")
    payslip = fields.Many2one('hr.payslip')
    name = fields.Char(string='Reference')
    amount = fields.Float(string="Amount")
    description = fields.Text(string='Description')
    date = fields.Date(string="Date", default=date.today())
