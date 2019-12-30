from odoo import models, api, fields, _
from odoo.exceptions import UserError


class AcademicCalenderLine(models.Model):
    _name = "academic.calender.line"
    _description = "Academic Calender Details"

    ENTRY_SEL = [
        ('holiday', 'Holiday'),
        ('exams', 'Exams'),
        ('activity', 'Activity'),
        ('other', 'Other'),
    ]

    @api.onchange('date_from')
    def onchange_account_asset(self):
        if self.date_from:
            self.date_to =  self.date_from

    @api.model
    def default_get(self, fields):
        res = super(AcademicCalenderLine, self).default_get(fields)
        year = self.env['school.year'].get_default_year()
        calender_id = self.env["academic.calender"].search([('school_year', '=', year)], limit=1)
        res['calender_id'] = calender_id and calender_id.id or False
        return res

    calender_id = fields.Many2one("academic.calender", "Calendar")
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    entry = fields.Char(string="Entry")
    entry_type = fields.Selection(ENTRY_SEL, string="Type", default="other")

##############################################################################


class AcademicCalender(models.Model):
    _name = "academic.calender"
    _description = "Academic Calender"
    _rec_name = "school_year"

    school_year = fields.Many2one("school.year", string="School Year", default=lambda self: self.env['school.year'].get_default_year())
    line_ids = fields.One2many("academic.calender.line", "calender_id")

    _sql_constraints = [
        ('unique_school_year',
         'unique(school_year)',
         'School Year Must be Unique per academic calender.'),
    ]

###############################################################################