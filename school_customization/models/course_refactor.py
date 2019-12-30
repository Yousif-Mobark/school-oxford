from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpAllStudentWizard(models.TransientModel):
    _inherit = "op.all.student"

    course_id = fields.Many2one(
        'op.course', 'Grade',
        default=lambda self: self.env['op.attendance.sheet'].browse(
            self.env.context['active_id']).register_id.course_id.id or False,
        readonly=True)

#################################################################


class FeesDetailReportWizard(models.TransientModel):
    _inherit = "fees.detail.report.wizard"

    course_id = fields.Many2one('op.course', 'Grade')

#################################################################


class OpBatch(models.Model):
    _inherit = "op.batch"

    course_id = fields.Many2one('op.course', 'Grade', required=True)

##################################################################


class OpStudentCourse(models.Model):
    _inherit = "op.student.course"

    course_id = fields.Many2one('op.course', 'Grade', required=True)

####################################################################


class OpClassroom(models.Model):
    _inherit = "op.classroom"

    course_id = fields.Many2one('op.course', 'Grade')

#####################################################################


class OpAdmissionRegister(models.Model):
    _inherit = "op.admission.register"

    course_id = fields.Many2one(
        'op.course', 'Grade', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, track_visibility='onchange')

    product_id = fields.Many2one(
        'product.product', 'Year Fees',
        domain=[('type', '=', 'service')])



####################################################################


class OpAdmission(models.Model):
    _inherit = "op.admission"

    course_id = fields.Many2one(
        'op.course', 'Grade', required=True,
        states={'done': [('readonly', True)]})

    prev_course_id = fields.Many2one(
        'op.course', 'Previous Grade', states={'done': [('readonly', True)]})

########################################################################


class AdmissionAnalysis(models.TransientModel):
    _inherit = "admission.analysis"

    course_id = fields.Many2one('op.course', 'Grade', required=True)

###########################################################################


class OpAttendanceRegister(models.Model):
    _inherit = "op.attendance.register"

    course_id = fields.Many2one(
        'op.course', 'Grade', required=True, track_visibility='onchange')


#333333########################################################################


class OpAttendanceSheet(models.Model):
    _inherit = "op.attendance.sheet"

    course_id = fields.Many2one(
        'op.course', related='register_id.course_id', store=True,
        readonly=True)
##################################################################


class OpAttendanceLine(models.Model):
    _inherit = "op.attendance.line"

    course_id = fields.Many2one(
        'op.course', 'Grade',
        related='attendance_id.register_id.course_id', store=True,
        readonly=True)
####################################################################


class OpAssignment(models.Model):
    _inherit = "op.assignment"

    course_id = fields.Many2one('op.course', 'Grade', required=True)

####################################################################

class SessionReport(models.TransientModel):
    _inherit = "time.table.report"

    course_id = fields.Many2one('op.course', 'Grade')

#############################################################


class GenerateSession(models.TransientModel):
    _inherit = "generate.time.table"

    course_id = fields.Many2one('op.course', 'Grade', required=True)

#############################################################


class OpSession(models.Model):
    _inherit = "op.session"

    course_id = fields.Many2one(
        'op.course', 'Grade', required=True)

#################################################################


class OpClassroom(models.Model):
    _inherit = "op.classroom"

    course_id = fields.Many2one('op.course', 'Grade')

####################################################################


class OpHeldExam(models.TransientModel):
    _inherit = "op.held.exam"

    course_id = fields.Many2one('op.course', 'Grade')


#########################################################################


class OpRoomDistribution(models.TransientModel):
    """ Exam Room Distribution """
    _inherit = "op.room.distribution"

    course_id = fields.Many2one("op.course", 'Grade')

########################################################################


class OpExam(models.Model):
    _inherit = "op.exam"

    course_id = fields.Many2one(
        'op.course', related='session_id.course_id', store=True,
        readonly=True)
####################################################################

class OpExamSession(models.Model):
    _inherit = "op.exam.session"

    course_id = fields.Many2one(
        'op.course', 'Grade', required=True, track_visibility='onchange')
#########################################################################


class OpExamAttendees(models.Model):
    _inherit = "op.exam.attendees"

    course_id = fields.Many2one('op.course', 'Grade', readonly=True)

#########################################################################


class OpSubjectRegistration(models.Model):
    _inherit = "op.subject.registration"

    course_id = fields.Many2one('op.course', 'Grade', required=True,
                                track_visibility='onchange')

######################################################################

