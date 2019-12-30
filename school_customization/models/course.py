from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpCourse(models.Model):
    _inherit = "op.course"

    sequence = fields.Integer('Sequence', default="100")

    def get_batch(self):
        print("==========================================%s"%self)
        year = self.env["school.year"].get_default_year()
        batch = self.env["op.batch"].search([('course_id', '=', self.id),
                                             ('year_id', '=', year)], limit=1)
        self.batch_id = batch

    batch_id = fields.Many2one("op.batch", compute=get_batch)

    _sql_constraints = [
        ('unique_classroom_code',
         'Check(1=1)', 'Code should be unique per classroom!')]

