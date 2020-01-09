# # -*- coding: utf-8 -*-

from odoo import fields, models, api

class excelConfigCompany(models.Model):
    _inherit = "res.company"

    device_id_col_name      = fields.Char(string = "Device ID Col Name")
    checkIn_date_col_name              = fields.Char(string = "Check In Date Col Name")
    checkIn_time_col_name              = fields.Char(string = "Check In Time Col Name")
    checkOut_date_col_name             = fields.Char(string = "Check Out Date Col Name")
    checkOut_time_col_name             = fields.Char(string = "Check Out Time Col Name")
    time_zone=fields.Integer()

