# -*- coding: utf-8 -*-
from odoo import fields, models, api

# Add Device id for the employee, that refere to the attendance id
class customEmplyeeDeviceId(models.Model):
    _inherit = "hr.employee"

    device_id = fields.Integer(string = "Device ID")



# Add this class to make the column name of any attendance device works well
# class attendanceDefaultConfiguration(models.Model):
#     _name = "attendance.default.configuration"

#     device_id_col_name                 = fields.Char(string = "Device ID Col Name")
#     checkIn_date_col_name              = fields.Char(string = "Check In Date Col Name" )
#     checkIn_time_col_name              = fields.Char(string = "Check In Time Col Name" )
#     checkOut_date_col_name             = fields.Char(string = "Check Out Date Col Name")
#     checkOut_time_col_name             = fields.Char(string = "Check Out Time Col Name")
