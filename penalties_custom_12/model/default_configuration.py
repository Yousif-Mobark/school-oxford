from ast import literal_eval

from odoo import models, fields, api

class DefaultConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'custom.penalty.config.settings'
    
    default_voucher_payable_account_id = fields.Many2one("account.account", string="Voucher Payable Account", domain=[('internal_type', '=', 'payable')])
    default_voucher_expense_account_id = fields.Many2one("account.account", string="Voucher Expense Account")
    default_journal_id = fields.Many2one("account.journal", string="Journal", domain=[('type', '=', 'purchase')])
    calc_formula = fields.Text(string="Calc Formula", default='''
#Available variables:
#employee_id : hr.employee
#contract : hr.contract
#result : the final result of this code (must be number).
result=(contract.wage/30)''')

    @api.model
    def get_values(self):
        res = super(DefaultConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        default_voucher_payable_account_id = literal_eval(ICPSudo.get_param('penalties_custom_12.default_voucher_payable_account_id', default='False'))
        default_voucher_expense_account_id = literal_eval(ICPSudo.get_param('penalties_custom_12.default_voucher_expense_account_id', default='False'))
        default_journal_id = literal_eval(ICPSudo.get_param('penalties_custom_12.default_journal_id', default='False'))
        calc_formula = literal_eval(ICPSudo.get_param('penalties_custom_12.calc_formula', default='False'))
        if default_voucher_payable_account_id and not self.env['account.account'].browse(default_voucher_payable_account_id).exists():
            default_voucher_payable_account_id = False

        if default_voucher_expense_account_id and not self.env['account.account'].browse(default_voucher_expense_account_id).exists():
            default_voucher_expense_account_id = False

        if default_journal_id and not self.env['account.account'].browse(default_journal_id).exists():
            default_journal_id = False
        res.update(
            default_voucher_payable_account_id=default_voucher_payable_account_id,
            default_voucher_expense_account_id=default_voucher_expense_account_id,
            default_journal_id=default_journal_id,
            calc_formula=calc_formula,
        )
        return res

    @api.model
    def set_values(self):
        super(DefaultConfiguration, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('penalties_custom_12.default_voucher_payable_account_id', default_voucher_payable_account_id.id)
        params.set_param('penalties_custom_12.default_voucher_expense_account_id', default_voucher_expense_account_id.id)
        params.set_param('penalties_custom_12.default_journal_id', default_journal_id.id)
        params.set_param('penalties_custom_12.calc_formula', calc_formula)



        
