from odoo import models, api, fields, _
from odoo.exceptions import UserError


class OpStudentFeesDetails(models.Model):
    _inherit = "op.student.fees.details"
    _description = "Student Fees Details"

    application_id = fields.Many2one("op.admission")

    @api.multi
    def get_invoice(self):
        self = self.sudo()
        """ Create invoice for fee payment process of student """
        inv_obj = self.env['account.invoice']
        partner_id = self.student_id.partner_id
        student = self.student_id
        account_id = False
        product = self.product_id
        if product.property_account_income_id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s".'
                  'You may have to install a chart of account from Accounting'
                  ' app, settings menu.') % product.name)
        if self.amount <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        else:
            amount = self.amount
            name = product.name

        invoice = inv_obj.create({
            'name': student.name,
            'student_id': self.student_id.id or False,
            'application_id': self.application_id.id or False,
            'origin': student.gr_no or False,
            'type': 'out_invoice',
            'reference': False,
            'account_id': partner_id.property_account_receivable_id.id,
            'partner_id': partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': student.gr_no,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': product.uom_id.id,
                'product_id': product.id,
            })],
        })
        invoice.compute_taxes()
        self.state = 'invoice'
        self.invoice_id = invoice.id
        return True