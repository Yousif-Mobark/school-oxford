
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class FeesInstalment(models.Model):
    _name = "fee.instalment"
    _description = "School Fees Instalment"
    _order = "sequence"

    admission_id = fields.Many2one("op.admission")
    sequence = fields.Integer("No.", default=1)
    amount = fields.Float("Amount")
    date = fields.Date("Date")
    payment_type = fields.Selection([('cash', 'Cash'), ('check', 'Cheque')])

################################################################


class SchoolFeesLines(models.Model):
    _name = "school.fee.line"
    _description = "School Fees Details"

    @api.depends("reg_fees", "book_fees", "school_fees", "activity_fees")
    def compute_fees(self):
        for rec in self:
            reg = rec.reg_fees or 0.0
            book = rec.book_fees or 0.0
            school = rec.school_fees or 0.0
            activity = rec.activity_fees or 0.0
            fees = reg + book + school + activity
            rec.fees = fees

    school_fee_id = fields.Many2one("school.fees", string="School Year Fees")
    course_id = fields.Many2one('op.course', 'Grade')
    reg_fees = fields.Float(string="Registration Fees")
    book_fees = fields.Float(string="Books and Uniform Fees")
    school_fees = fields.Float(string="School Fees")
    activity_fees = fields.Float(string="Activity Fees")
    fees = fields.Float(string="Fees", compute="compute_fees")
    product_id = fields.Many2one("product.product", string="Product", domain=[('type', '=', 'service')])

######################################################################################################


class SchoolFees(models.Model):
    _name = "school.fees"
    _description = "School Fees"

    CATE_SEL = [
        ('standard', 'Local'),
        ('foreign', 'Foreign '),
        ('new', 'New Admission')
    ]

    @api.multi
    @api.depends("year_id", "category")
    def _compute_name(self):
        for rec in self:
            if rec.year_id or rec.category:
                cate = str(rec.category) or ""
                rec.name = str(rec.year_id.display_name + " - " + cate)

    @api.multi
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.read(['year_id', 'category'])
        return [(fees.id, '%s%s' % (fees.year_id.display_name and '%s-' % fees.category or '', fees.year_id.display_name))
                for fees in self]

    name = fields.Char(string="Name", compute="_compute_name")
    year_id = fields.Many2one("school.year", "School Year",
                              default= lambda self: self.env['school.year'].get_default_year())
    category = fields.Selection(CATE_SEL, string="Category", default='standard')
    lines = fields.One2many("school.fee.line", "school_fee_id")
    active = fields.Boolean(string="Active", default=True)


