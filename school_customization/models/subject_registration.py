
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpSubjectRegistration(models.Model):
    _inherit = "op.subject.registration"

    @api.multi
    def action_submitted(self):
        self.action_approve()
        self.state = 'submitted'

    @api.onchange('course_id')
    def onchange_course(self):
        self.batch_id = self.course_id.batch_id
