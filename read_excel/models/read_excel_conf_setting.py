# # -*- coding: utf-8 -*-

from odoo import fields, models, api

class excelConfigCompany(models.Model):
    _inherit = "res.company"

    device_id_col_name      = fields.Char(string = "Device ID Col Name")
    checkIn_date_col_name              = fields.Char(string = "Check In Date Col Name")
    checkIn_time_col_name              = fields.Char(string = "Check In Time Col Name")
    checkOut_date_col_name             = fields.Char(string = "Check Out Date Col Name")
    checkOut_time_col_name             = fields.Char(string = "Check Out Time Col Name")


# PARAMS = {
#     "deviceID": "attendance.default.configuration.device_id_col_name",
#     "checkInDate": "attendance.default.configuration.checkIn_date_col_name",
#     "checkInTime": "attendance.default.configuration.checkIn_time_col_name",
#     "checkOutDate": "attendance.default.configuration.checkOut_date_col_name",
#     "checkOutTime": "attendance.default.configuration.checkOut_time_col_name"
# }


# class excelConfigSetting(models.TransientModel):
#     _inherit = "res.config.settings"
#     # _name = "excel.confg.setting"

#     device_id_col_name      = fields.Char(string = "Device ID Col Name")
#     checkIn_date_col_name              = fields.Char(string = "Check In Date Col Name")
#     checkIn_time_col_name              = fields.Char(string = "Check In Time Col Name")
#     checkOut_date_col_name             = fields.Char(string = "Check Out Date Col Name")
#     checkOut_time_col_name             = fields.Char(string = "Check Out Time Col Name")


#     @api.multi
#     def set_params(self):
#         self.ensure_one()
        
#         for field_name, key_name in PARAMS:
#             value = getattr(self, field_name, '').strip()
#             self.env["ir.set_parameter"].set_param(key_name, value)

    
#     def get_default_params(self, fields):
#         res = {}
#         for field_name , key_name in PARAMS:
#             res[field_name] = self.env['ir.congfig_parameter'].get_param(key_name, '').strip()