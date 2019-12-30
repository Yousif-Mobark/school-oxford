from odoo import models, fields, api


class OpAttendanceSheet(models.Model):
    _inherit = "op.attendance.sheet"

    _sql_constraints = [
        ('unique_register_sheet_day',
         'unique(register_id,attendance_date)',
         'Sheet must be unique per Register/Date.'),
    ]
