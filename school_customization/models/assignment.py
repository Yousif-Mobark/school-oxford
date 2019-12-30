from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpAssignment(models.Model):
    _inherit = "op.assignment"


    @api.onchange('course_id')
    def onchange_course(self):
        course = self.course_id
        batch = course.batch_id
        self.batch_id = batch

        self.allocation_ids = self.env["op.student"].search(
            [('course_detail_ids.course_id', '=', course.id),('course_detail_ids.batch_id','=',batch.id)])

        faculty = self.faculty_id
        if self.course_id:
            subject_ids = self.env['op.course'].search([
                ('id', '=', self.course_id.id)]).subject_ids

            subject_ids = subject_ids.filtered(lambda x: x in faculty.faculty_subject_ids)
            return {'domain': {'subject_id': [('id', 'in', subject_ids.ids)]}}
