from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo.exceptions import ValidationError, UserError



class TransportationLine(models.Model):
    _name = "transportation.line"

    student_id = fields.Many2one("op.student", "Student", required=1)
    course_id = fields.Many2one("op.course", "Grade", related="student_id.course_id", required=1)
    fees = fields.Float("Monthly Fees", required=1)
    transport_id = fields.Many2one("transportation", "Transportation")
    notes = fields.Text("Notes")
    invoice_id = fields.Many2one("account.invoice")

#####################################################################################


class Transportation(models.Model):
    _name = "transportation"

    STATE_SEL = [
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('done', 'Done')
    ]

    MONTH_SEL = [
        ('1', "January"),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]

    name = fields.Char("Name", required=1)
    year_id = fields.Many2one("school.year", "School Year",
                              default=lambda self: self.env['school.year'].get_default_year())
    car_type = fields.Char("Car Type", required=1)
    driver_name = fields.Char("Driver Name", required=1)
    month = fields.Selection(MONTH_SEL, "Month", required=1)
    monthly_fees = fields.Float("Monthly Fees")
    area = fields.Char("Area", required=1)
    lines = fields.One2many("transportation.line", "transport_id")
    state = fields.Selection(STATE_SEL, string='Status',
                             readonly=True, copy=False,
                             index=True, track_visibility='onchange', track_sequence=3, default='draft')

    @api.multi
    @api.constrains('monthly_fees')
    def _check_monthly_fees(self):
        for record in self:
            if record.monthly_fees <= 0:
                raise ValidationError(_('Invalid Amount for monthy fees'))

    @api.multi
    def action_validate(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'validate'

    def create_invoice(self, line, partner_id):
        inv_obj = self.env['account.invoice']
        company = self.env.user.company_id
        product = company.transport_product_id

        if not product:
            raise UserError("Proper Company Configuration is missing product! can not produce student invoice")
        if product.id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". \
                           You may have to install a chart of account from Accounting \
                           app, settings menu.') % (product.name,))

        if line.fees <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        else:
            amount = line.fees
            name = product.name
        invoice = inv_obj.create({
            'name': self.name,
            'origin': self.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': partner_id.property_account_receivable_id.id,
            'partner_id': partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': self.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0,
                'uom_id': product.uom_id.id,
                'product_id': product.id,
            })],
        })
        invoice.compute_taxes()
        return invoice

    def action_invoice_lines(self):
        for rec in self:
            lines = rec.lines
            for line in lines:
                student = line.student_id
                partner = student.user_id.partner_id
                line.invoice_id = self.create_invoice(line, partner)
            self.state = 'done'






