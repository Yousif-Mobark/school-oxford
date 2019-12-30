from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree


class TimetableStudent(models.Model):
    _name = "timetable.student"
    _description = "Time Table Student"

    @api.multi
    def name_get(self):
        return [(record.id, "Student Timetable") for record in self]


######################################################################################################


class TimetableFaculty(models.Model):
    _name = "timetable.faculty"
    _description = "Time Table Faculty"

    @api.multi
    def name_get(self):
        return [(record.id, "Faculty Timetable") for record in self]

######################################################################################################


class TimetableClassroom(models.Model):
    _name = "timetable.classroom"
    _description = "Time Table Classroom"

    @api.multi
    def name_get(self):
        return [(record.id, "Classroom Timetable") for record in self]
