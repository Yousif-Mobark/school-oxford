from datetime import timedelta

from odoo import models, fields, api


class AttendanceSheetGenerate(models.TransientModel):
    _name = "attendance.sheet.generate"
    _description = "Generate attendance sheets"

    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    attendance_reg_id = fields.Many2one("op.attendance.register", "Attendance Grade", required=True)

    def get_lines(self, students):
        lines = []
        for student in students:
            values = [0, False,{
                'student_id': student.id,

            }]
            lines.append(values)
        return lines




    def do_generate_sheet(self):
        from_date = self.from_date
        to_date = self.to_date
        period = to_date - from_date
        days = period.days
        sheet_obj = self.env["op.attendance.sheet"]
        register = self.attendance_reg_id
        course = register.course_id
        students = self.env["op.student"].search([("course_id", '=', course.id)])
        lines = self.get_lines(students)
        for day in range(0, days+1):
            date = from_date + timedelta(days=day)
            name = course and (str(date) + course.name) or str(date)
            vals = {
                'name': name,
                'attendance_date': date,
                'attendance_line':  lines,
                'register_id': register.id,
            }
            sheet_obj.create(vals)
