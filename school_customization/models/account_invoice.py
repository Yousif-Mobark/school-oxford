
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero


class AccountInvocie(models.Model):
    _inherit = "account.invoice"

    student_id = fields.Many2one("op.student", string="Student Profile")
    application_id = fields.Many2one("op.admission")


