from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpBatch(models.Model):
    _inherit = "op.batch"

    year_id = fields.Many2one("school.year", string="School Year", default= lambda self: self.env['school.year'].get_default_year())
    start_date = fields.Date(
        'Start Date', related="year_id.start_date")
    end_date = fields.Date('End Date', related="year_id.end_date")


    _sql_constraints = [
        ('year_grade_uniq',
         'unique (year_id,course_id)',
         'Grade in School Year batch must be unique!')
    ]


