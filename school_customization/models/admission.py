import random
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare

DUMMY_DOMAIN = "soa.com"


def get_percentage(total, part):
    return (part * 100) / total


class OpAdmission(models.Model):
    _inherit = "op.admission"

    ID_SEL = [
        ('national_no', 'National Number'),
        ('national_card', 'National Card'),
        ('passport', 'Passport')]

    LANG_SEL = [

        ('en', 'English'),
        ('ar', 'Arabic'),
        ('fr', 'French'),
        ('sp', 'Spanish'),
        ('other', 'Other'),
    ]

    RELIGION_SEL = [

        ('islam', 'Islam'),
        ('christian', 'Christianity'),
        ('other', 'Other'),
    ]

    TYPE_SEL = [
        ('standard', 'Local'),
        ('foreign', 'Foreign '),
        ('new', 'New Admission')
    ]

    @api.depends('register_id', 'admission_type')
    def get_fees(self):
        for rec in self:
            year = rec.year_id
            course = rec.course_id
            admission_type = rec.admission_type
            if year and course:
                fees_line = self.env["school.fee.line"].search([('school_fee_id.year_id', '=', year.id),
                                                                ('course_id', '=', course.id),
                                                                ('school_fee_id.category', '=', admission_type)],
                                                               limit=1)
                rec.fees_line_id = fees_line

    def _get_batch(self):
        year = self.year_id
        grade = self.course_id
        batch = self.env["op.batch"].search([("year_id", "=", year.id), ("course_id", "=", grade.id)], limit=1)
        return batch

    @api.onchange('course_id')
    def onchange_course(self):
        course_id = self.course_id
        self.batch_id = False
        term_id = False
        if self.course_id and self.course_id.fees_term_id:
            term_id = self.course_id.fees_term_id
        self.fees_term_id = term_id
        course = self.env["op.course"].browse(course_id.id)
        self.batch_id = course.batch_id

    def get_siblings_discount(self):
        discounts = self.discount_ids
        total_percentage = 0
        for discount in discounts.filtered(lambda r: r.type == 'percentage'):
            total_percentage += discount.percentage
        for discount in discounts.filtered(lambda r: r.type == 'fixed'):
            percentage = self.get_percentage(discount.amount)
            total_percentage += percentage
        return total_percentage

    @api.onchange('school_fees', 'discount_ids', 'percentage_discount', "amount_discount")
    def onchange_discounts(self):
        for rec in self:
            school_fees = rec.school_fees or 0
            fees = rec.fees or 0
            # sibling discount from overall fees
            siblings_discount = self.get_siblings_discount() or 0
            siblings_discount_amount = ((school_fees * siblings_discount) / 100)
            # percentage discount from overall fees
            percentage_discount = self.percentage_discount or 0
            percentage_discount_amount = ((fees * percentage_discount) / 100)
            # direct discount
            direct_discount_amount = rec.amount_discount or 0
            discount = percentage_discount_amount + siblings_discount_amount + direct_discount_amount

            rec.actual_school_fees = school_fees - discount

    @api.depends("actual_school_fees")
    def compute_actual_fees(self):
        for rec in self:
            reg = rec.reg_fees or 0.0
            book = rec.book_fees or 0.0
            school = rec.actual_school_fees or 0.0
            activity = rec.activity_fees or 0.0
            fees = reg + book + school + activity
            rec.actual_fees = fees
            ###
            if rec.paid_reg:
                remaining_fees = fees - rec.register_amount_paid
                rec.remain_fees = remaining_fees

    @api.depends("name", "middle_name", "third_name", "last_name")
    def _compute_full_name(self):
        for rec in self:
            full_name = ''
            names = [rec.name, rec.middle_name, rec.third_name, rec.last_name]
            if rec.name and rec.middle_name and rec.third_name and rec.last_name:
                for name in names:
                    full_name += name + " "
                rec.full_name = full_name
            else:
                rec.full_name = names[0]

    # names
    third_name = fields.Char(
        'Third Name', size=128,
        states={'done': [('readonly', False)]})
    full_name = fields.Char(string="Full Name", compute="_compute_full_name")

    ar_first_name = fields.Char(string="First Name", size=128)
    ar_middle_name = fields.Char(string="Second Name", size=128)
    ar_third_name = fields.Char(string="Third Name", size=128)
    ar_last_name = fields.Char(string="Last Name", size=128)

    id_type = fields.Selection(ID_SEL, string="ID type")
    id_file = fields.Binary(string='ID Picture')

    # # Only reg not yet in student
    # basic info
    place_of_birth = fields.Char("Place of Birth")
    primary_lang = fields.Selection(LANG_SEL, "Mother Tongue")
    lang = fields.Char("Language")

    nationality_id = fields.Many2one("res.country", "Nationality")
    religion = fields.Selection(RELIGION_SEL, "Religion")
    other_religion = fields.Char("Other Religion")
    year_id = fields.Many2one("school.year", related="register_id.year_id")
    admission_type = fields.Selection(TYPE_SEL, "Admission Type", default="standard", required=True)
    blood_group = fields.Selection([
        ('A+', 'A+ve'),
        ('B+', 'B+ve'),
        ('O+', 'O+ve'),
        ('AB+', 'AB+ve'),
        ('A-', 'A-ve'),
        ('B-', 'B-ve'),
        ('O-', 'O-ve'),
        ('AB-', 'AB-ve')
    ], string='Blood Group')

    # legal and medical
    restraining_order = fields.Boolean("Restraining Order")
    is_medical_issue = fields.Boolean("Medical Issues")
    medical = fields.Text("Issues")
    guardian_name = fields.Char("Guardian Name")
    guardian_relation = fields.Char("Relationship")
    guardian_phone = fields.Char("Phone No.")
    nok_1 = fields.Char("Relative Mobile (1)")
    nok_2 = fields.Char("Relative Mobile (1)")

    # parents
    mother_id = fields.Many2one("op.parent", string="Mother Name")
    father_id = fields.Many2one("op.parent", string="Father Name")

    # discount
    discount_ids = fields.Many2many("fee.discount", string="Discounts")
    percentage_discount = fields.Float("Percentage Discount")
    amount_discount = fields.Float("Amount Discount")
    # fees
    fees_line_id = fields.Many2one("school.fee.line", "Fees", compute="get_fees")
    reg_fees = fields.Float(string="Registration Fees", related="fees_line_id.reg_fees")
    book_fees = fields.Float(string="Books and Uniform Fees", related="fees_line_id.book_fees")
    school_fees = fields.Float(string="School Fees", related="fees_line_id.school_fees")
    activity_fees = fields.Float(string="Activity Fees", related="fees_line_id.activity_fees")
    fees = fields.Float(string="Total Fees", related="fees_line_id.fees")
    # actual fees
    actual_school_fees = fields.Float("School Fees with Discount", default=lambda self: self.school_fees)
    actual_fees = fields.Float("Fees after Discount", compute="compute_actual_fees")
    remain_fees = fields.Float("Remaining Fees", compute="compute_actual_fees")
    # registration
    paid_reg = fields.Boolean("Paid Registration Fees", readonly=1)
    register_amount_paid = fields.Float("Registration Paid Amount", readonly=1, default=0)
    # installments
    instalment_ids = fields.One2many("fee.instalment", "admission_id", "Installments")
    # accounting
    invoice_id = fields.Many2one("account.invoice", string="Student Invoice")
    res_invoice_id = fields.Many2one("account.invoice", string="Student Invoice")
    # transportation
    need_transportation = fields.Boolean("Need Transportation", default=False)
    # change required
    mobile = fields.Char(
        'Mobile', size=16,
        states={'done': [('readonly', True)], 'submit': [('required', False)]})
    email = fields.Char(
        'Email', size=256, required=False,
        states={'done': [('readonly', True)]})
    phone = fields.Char(
        'Phone', size=16, states={'done': [('readonly', True)],

                                  'submit': [('required', False)]})

    @api.one
    @api.constrains('instalment_ids')
    def _check_installments(self):
        instalments = self.instalment_ids
        if instalments:
            total_instalments = instalments.mapped("amount")
            if float_compare(sum(total_instalments), self.actual_fees, precision_digits=2):
                raise ValidationError(
                    _('Please make sure the total of the installments is equal to the actual fees'))

    # # #####################################################################################

    def submit_form(self):
        student_name = self.first_name + ' ' + self.middle_name + ' ' + self.third_name + ' ' + self.last_name
        student = self.env['op.student'].create({'name': student_name, 'gender': self.gender,
                                                 'birth_date': self.birth_date, 'blood_group': self.blood_group,
                                                 'first_name': self.first_name, 'middle_name': self.middle_name,
                                                 'third_name': self.third_name, 'last_name': self.last_name,
                                                 'nationality': self.nationality_id.id, 'email': self.email,
                                                 'mobile': self.mobile, 'phone': self.phone, 'street': self.street,
                                                 'street2': self.street2, 'city': self.city, 'zip': self.zip,
                                                 'country_id': self.country_id, 'state_id': self.state_id,
                                                 'religion': self.religion})
        self.student_id = student.id
        self.state = 'submit'
        self.admission_confirm()

    def register_student(self):
        self = self.sudo()
        for record in self:
            if record.register_id.max_count:
                total_admission = self.env['op.admission'].search_count(
                    [('register_id', '=', record.register_id.id),
                     ('state', '=', 'done')])
                if not total_admission < record.register_id.max_count:
                    msg = 'Max Admission In Admission Register :- (%s)' % (
                        record.register_id.max_count)
                    raise ValidationError(_(msg))
            # create student !
            if not record.student_id:
                vals = record.get_student_vals()
                record.partner_id = self.env['res.users'].browse(
                    vals.get('user_id')).partner_id.id

                student_id = self.env['op.student'].create(vals).id
                student_obj = self.env["op.student"].browse(student_id)
                # record.partner_id.write({"name": student_obj.full_name})
            else:
                student_id = record.student_id.id
                record.student_id.write({
                    'course_detail_ids': [[0, False, {
                        'course_id':
                            record.course_id and record.course_id.id or False,
                        'batch_id':
                            record.batch_id and record.batch_id.id or False,
                    }]],
                })

            record.write({
                'student_id': student_id,
            })

    @api.multi
    def enroll_student(self):
        self = self.sudo()
        for record in self:
            # create student !
            student_id = record.student_id.id
            if record.fees_term_id:
                val = []
                product_id = record.register_id.product_id.id
                for line in record.fees_term_id.line_ids:
                    no_days = line.due_days
                    per_amount = line.value
                    amount = (per_amount * record.remain_fees) / 100
                    date = (datetime.today() + relativedelta(
                        days=no_days)).date()
                    dict_val = {
                        'fees_line_id': line.id,
                        'amount': amount,
                        'date': date,
                        'product_id': product_id,
                        'state': 'draft',
                        'application_id': record.id,
                    }
                    val.append([0, False, dict_val])
                self.env['op.student'].browse(student_id).write({
                    'fees_detail_ids': val
                })
            record.write({
                'nbr': 1,
                'state': 'done',
                'admission_date': fields.Date.today(),
            })
            reg_id = self.env['op.subject.registration'].create({
                'student_id': student_id,
                'batch_id': record.batch_id.id,
                'course_id': record.course_id.id,
                'min_unit_load': record.course_id.min_unit_load or 0.0,
                'max_unit_load': record.course_id.max_unit_load or 0.0,
                'state': 'draft',
            })
            reg_id.get_subjects()
            if 'elective' not in reg_id.course_id.subject_ids.mapped("subject_type"):
                reg_id.action_submitted()

    def get_student_email(self):
        std_num = self.env['ir.sequence'].next_by_code(
            'op.student') or random.randint(1, 10001)
        email = str(std_num) + "@" + DUMMY_DOMAIN
        return std_num, email

    def get_parents(self):
        parents = []
        mother = self.mother_id
        father = self.father_id
        if mother:
            parents.append((4, self.mother_id.id))
        if father:
            parents.append((4, self.father_id.id))
        return parents or False

    @api.multi
    def get_student_vals(self):
        for student in self:
            [gr_no, email] = self.get_student_email()
            student_user = self.env['res.users'].create({
                'name': student.full_name or student.name,
                'login': email,
                'image': self.image or False,
                'company_id': self.env.ref('base.main_company').id,
                'groups_id': [
                    (6, 0,
                     [self.env.ref('openeducat_core.group_op_student').id, self.env.ref('base.group_portal').id])]
            })
            details = {
                'current_grade': student.course_id.id,
                'phone': student.phone,
                'mobile': student.mobile,
                'email': student.email,
                'blood_group': student.blood_group,
                'id_type': student.id_type,
                'id_file': student.id_file,
                'place_of_birth': student.place_of_birth,
                "primary_lang": student.primary_lang,
                "lang_other": student.lang,
                "religion": student.religion,
                "other_religion": student.other_religion,
                'street': student.street,
                'street2': student.street2,
                'city': student.city,
                'nationality': student.nationality_id.id,
                'country_id':
                    student.country_id and student.country_id.id or False,
                'state_id': student.state_id and student.state_id.id or False,
                'image': student.image,
                'zip': student.zip,
                'parent_ids': self.get_parents(),
                'course_id': student.course_id.id,
                'batch_id': student.batch_id.id,
                'gr_no': gr_no,
            }
            student_user.partner_id.write(details)
            details.update({
                'title': student.title and student.title.id or False,

                'first_name': student.name,
                'middle_name': student.middle_name,
                'third_name': student.third_name,
                'last_name': student.last_name,
                'ar_first_name': student.ar_first_name,
                'ar_middle_name': student.ar_middle_name,
                'ar_third_name': student.ar_third_name,
                'ar_last_name': student.ar_last_name,
                'name': student.full_name or student.name,

                'birth_date': student.birth_date,
                'gender': student.gender,
                'course_id':
                    student.course_id and student.course_id.id or False,
                'batch_id':
                    student.batch_id and student.batch_id.id or False,
                'image': student.image or False,
                'course_detail_ids': [[0, False, {
                    'date': fields.Date.today(),
                    'course_id':
                        student.course_id and student.course_id.id or False,
                    'batch_id':
                        student.batch_id and student.batch_id.id or False,
                }]],
                'user_id': student_user.id,
            })
            return details

    @api.multi
    def create_invoice(self):
        """ Create invoice for fee payment process of student """

        inv_obj = self.env['account.invoice']
        partner_id = self.env['res.partner'].create({'name': self.name})

        account_id = False
        product = self.fees_line_id.product_id
        if not product:
            raise UserError("Proper Accounting Configuration is missing product! can not produce student invoice")
        if product.id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". \
                   You may have to install a chart of account from Accounting \
                   app, settings menu.') % (product.name,))

        if self.fees <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        else:
            amount = self.actual_fees
            name = product.name
        # discount = self.get_discount_total()
        invoice = inv_obj.create({
            'name': self.name,
            'origin': self.application_number,
            'type': 'out_invoice',
            'reference': False,
            'account_id': partner_id.property_account_receivable_id.id,
            'partner_id': partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': self.application_number,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0,
                'uom_id': self.register_id.product_id.uom_id.id,
                'product_id': product.id,
            })],
        })
        invoice.compute_taxes()

        form_view = self.env.ref('account.invoice_form')
        tree_view = self.env.ref('account.invoice_tree')
        value = {
            'domain': str([('id', '=', invoice.id)]),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'view_id': False,
            'views': [(form_view and form_view.id or False, 'form'),
                      (tree_view and tree_view.id or False, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': invoice.id,
            'target': 'current',
            'nodestroy': True
        }
        self.partner_id = partner_id
        self.state = 'done'
        self.invoice_id = invoice
        return value

    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that
        display existing invoices of given student ids and show a invoice"
        '''
        result = self.env.ref('account.action_invoice_tree1')
        id = result and result.id or False
        result = self.env['ir.actions.act_window'].browse(id).read()[0]
        for rec in self:
            inv_id = rec.invoice_id
            result['context'] = {'default_partner_id': rec.student_id.partner_id.id}

        res = self.env.ref('account.invoice_form')
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = inv_id.id or False
        print(result['res_id'])
        return result


###############################################


class OpAdmissionRegister(models.Model):
    _inherit = "op.admission.register"

    start_date = fields.Date(
        'Start Date', required=False)
    end_date = fields.Date(
        'End Date', required=False)
    year_id = fields.Many2one("school.year", "School Year",
                              default=lambda self: self.env['school.year'].get_default_year())
    product_id = fields.Many2one(
        'product.product', 'Year Fees',
        domain=[('type', '=', 'service')])

    @api.multi
    def confirm_register(self):
        self.state = 'admission'
