from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError


class CreateRegisterInvoice(models.TransientModel):
    _name = "register.invoice"
    _description = "Create Registration Invoice"

    @api.model
    def default_get(self, fields):
        res = super(CreateRegisterInvoice, self).default_get(fields)
        res_id = self._context.get('active_id')
        if not res_id:
            raise UserError("No student linked to this !")

        admission = self.env["op.admission"].browse(res_id)
        # student = admission.student_id
        fees = admission.reg_fees
        res.update({
            'application_id': admission.id,
            'student_id': admission.student_id.id,
            'reg_amount': fees,
        })
        return res

    application_id = fields.Many2one("op.admission", string="Application")
    student_id = fields.Many2one("op.student", string="Student")
    reg_amount = fields.Float("Registration Amount")

    def create_invoice(self, partner_id):
        application = self.application_id

        inv_obj = self.env['account.invoice']
        company = self.env.user.company_id
        product = company.registration_product_id
        if not product:
            raise UserError("Proper company Configuration is missing product! can not produce student invoice")
        if product.id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". \
                                  You may have to install a chart of account from Accounting \
                                  app, settings menu.') % (product.name,))

        if self.reg_amount <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        else:
            amount = self.reg_amount
            name = product.name
        invoice = inv_obj.create({
            # 'name': self.name,
            'type': 'out_invoice',
            'reference': False,
            'date_invoice': fields.Date.today(),
            'student_id': application.student_id.id or False,
            'application_id': application.id or False,
            'origin': application.student_id.gr_no or False,
            'account_id': partner_id.property_account_receivable_id.id,
            'partner_id': partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': self.application_id.application_number,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0,
                'uom_id': product.uom_id.id,
                'product_id': product.id,
            })],
        })
        print("###################################################################")
        invoice.compute_taxes()
        return invoice

    def do_issue_invoice(self):
        application = self.application_id
        if application.paid_reg:
            raise UserError("Student has already been issued an invoice for registration")
        else:
            fees = self.reg_amount
            if fees <= 0:
                raise UserError("Incorrect fees amount")
            application.register_student()
            student = application.student_id
            partner = student.user_id.partner_id
            invoice = self.create_invoice(partner)
            application_vals = {
                'res_invoice_id': invoice.id,
                'paid_reg': True,
                'register_amount_paid': fees
            }
            application.write(application_vals)
