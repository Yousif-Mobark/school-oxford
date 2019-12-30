from odoo import models, fields, api, _


class AccConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_gm_approve = fields.Boolean(default=False, string="Approval from General Manager",
                                  help="Loan Approval from general manager")

    @api.model
    def get_values(self):
        res = super(AccConfig, self).get_values()
        res.update(
            loan_gm_approve=self.env['ir.config_parameter'].sudo().get_param('loan_gm_approve')

        )
        return res

    @api.multi
    def set_values(self):
        super(AccConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('loan_gm_approve', self.loan_gm_approve)

