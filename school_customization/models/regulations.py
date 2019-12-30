
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class RegulationLine(models.Model):
    _name = "regulation.line"
    _description = "Regulation Details"

    regulation_id = fields.Many2one("school.regulation")
    sequence = fields.Integer("No.")
    description = fields.Text("Regulation")


# ###########################################################


class SchoolRegulation(models.Model):
    _name = "school.regulation"
    _description = "School Regulation"

    REG_SEL = [

        ('academic', 'Academic'),
        ('hr', 'HR'),
    ]
    name = fields.Char("Name")
    regulation_type = fields.Selection(REG_SEL, string="Regulation Type")
    date = fields.Date("Date")
    line_ids = fields.One2many("regulation.line", "regulation_id", "Regulations")
############################################################################################

# regulation and policies PDF models
#
##################################################################


class AcademicRegulationFrame(models.Model):
    _name = "academic.regulation.frame"
    _description = "School Academic Regulation PDF"

    @api.multi
    def name_get(self):
        return [(record.id, "Academic Regulations") for record in self]


#########################################


class HrPolicyFrame(models.Model):
    _name = "hr.policy.frame"
    _description = "School HR Policy PDF"

    @api.multi
    def name_get(self):
        return [(record.id, "HR Policies") for record in self]
