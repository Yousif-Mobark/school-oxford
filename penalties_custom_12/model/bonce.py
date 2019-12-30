from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import except_orm, Warning, UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class Bonce(models.Model):
    _name = "bonce.bonce"
    _inherit = 'mail.thread'

    name = fields.Char(string='Reference', required=True)
    bonce_no = fields.Char(string='Sequence', readonly=True)
    date = fields.Date(string="Date", default=date.today())
    employee = fields.Many2one('hr.employee', string="Employee", required=True)
    bonce_type = fields.Many2one('bonce.type', string='Bonce Type', required=True)
    fix_formula = fields.Selection([('formula', 'Formula'), ("fix", "Fixed")], string='Fix/Formula', required=True)
    amount = fields.Float(string="Amount", track_visibility='onchange')
    description = fields.Text(string='Description', required=True)
    state = fields.Selection([('draft', 'Draft'), ("confirm", "Confirm"),
                              ('hr_manager', 'Hr Manager'),
                              ('done', 'Done')], default='draft', string='State', track_visibility='onchange')
    voucher_ref = fields.Many2one('account.voucher', string='Voucher reference', readonly=True)
    is_paid = fields.Boolean()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(
                    _('You cannot delete form which is not is draft.'))
        return super(Bonce, self).unlink()

    @api.model
    def create(self, vals):
        res = super(Bonce, self).create(vals)
        next_seq = self.env['ir.sequence'].get('bonce.no')
        res.update({'bonce_no': next_seq})
        return res

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.amount <= 0:
                if rec.fix_formula != 'fix':
                    raise ValidationError("Please click on calc amount button, and amount must be greater than zero")
                raise ValidationError(_("Amount Must Be Greater Than Zero"))
            if rec.state == 'draft':
                rec.state = 'confirm'
                if rec.bonce_type.pay_included == 'voucher':
                    self.generate_voucher()
            else:
                raise UserError("In order to confirm this bonce state must be in draft")

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

        if self.bonce_type.pay_included == 'voucher':
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

    @api.multi
    def action_hr_approval(self):
        for rec in self:
            if rec.state == 'confirm':
                self.state = 'hr_manager'
            else:
                raise UserError(_("In order of hr approve state must be in confirm"))

    @api.multi
    def action_ceo_approve(self):
        for rec in self:
            if rec.state == 'hr_manager':
                self.state = 'done'
            else:
                raise UserError(_("In order for ceo approve, state must be in hr manager"))

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

    def set_amount(self):
        for rec in self:
            amount = self.calc_amount(employee_id=rec.employee, contract=rec.employee.contract_id, rec=self).get('result', False)
            rec.amount = amount

    @api.model
    def _default_calc_formula(self):
        calc_formula = self.env['ir.config_parameter'].sudo().get_param(
            'penalties_custom_12.calc_formula')
        return calc_formula

    def calc_amount(self, employee_id, contract, rec):
        employee = self.env['hr.employee'].browse(employee_id)
        formula_data = self._default_calc_formula()
        if not formula_data:
            raise ValidationError("Please Check payroll Configuration. Set formula")
        localdict = {"employee_id": employee, "contract": contract, "bounce": self, "type": rec, 'result': 0}
        safe_eval(formula_data, localdict, mode='exec', nocopy=True)
        return localdict


class BonceType(models.Model):
    _name = 'bonce.type'
    _inherit = 'mail.thread'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    pay_included = fields.Selection([('payslip', 'Payslip'), ("voucher", "Voucher")], string='Bonce Type',
                                    default='payslip')

    def toggle_active(self):
        """ When re-activating leads and opportunities set their probability
        to the default stage one. """
        res = super(BonceType, self).toggle_active()
        return res


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    bonce = fields.Float(string='Bonce', compute='compute_bon', store=True)
    bonce_line = fields.One2many('bonce.line', 'payslip', string='Bonce lines')

    @api.onchange('employee_id')
    def payslip_bonce(self):
        employee_bonce_ids = self.env['bonce.bonce'].search([('employee', '=', self.employee_id.id),
                                                             ('is_paid', '=', False),
                                                             ('state', '=', 'done')])
        if self.bonce_line:
            self.bonce_line.sudo().unlink()
        lines = self.bonce_line.browse()
        for bonce in employee_bonce_ids:
            if bonce.bonce_type.pay_included == 'payslip':
                lines += lines.new({
                    'bonce_id': bonce.id,
                    'payslip': self.id,
                    'name': bonce.name,
                    'amount': bonce.amount,
                    'description': bonce.description,
                    'date': bonce.date,
                })
        self.bonce_line = lines

    @api.multi
    def action_payslip_done(self):
        for rec in self:
            for line in rec.bonce_line:
                line.bonce_id.is_paid = True
        return super(Payslip, self).action_payslip_done()

    @api.depends('bonce_line')
    def compute_bon(self):
        for rec in self:
            for lin in rec.bonce_line:
                rec.bonce += lin.amount


class BonceLine(models.Model):
    _name = 'bonce.line'

    bonce_id = fields.Many2one("bonce.bonce")
    payslip = fields.Many2one('hr.payslip')
    name = fields.Char(string='Reference')
    amount = fields.Float(string="Amount")
    description = fields.Text(string='Description')
    date = fields.Date(string="Date", default=date.today())
