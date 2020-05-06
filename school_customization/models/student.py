from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpStudent(models.Model):
    _inherit = "op.student"

    ID_SEL = [
        ('national_no', 'National Number'),
        ('national_card', 'National Card'),
        ('passport', 'Passport')]

    LANG_SEL = [

        ('en', 'English'),
        ('ar', 'Arabic'),
        ('fr', 'French'),
        ('sp', 'Spanish'),
        ('other', 'Other'),
    ]

    RELIGION_SEL = [

        ('islam', 'Islam'),
        ('christian', 'Christianity'),
        ('other', 'Other'),
    ]

    # @api.multi
    # def name_get(self):
    #     # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
    #     self.read(["name", "middle_name", "third_name", "last_name"])
    #     return [(student.id, '%s' % (student.full_name))
    #             for student in self]

    @api.depends("name", "middle_name", "third_name", "last_name")
    def _compute_full_name(self):
        for rec in self:
            full_name = ''
            names = [rec.first_name, rec.middle_name, rec.third_name, rec.last_name]
            if rec.name and rec.middle_name and rec.third_name and rec.last_name:
                for name in names:
                    full_name += name + " "
                rec.full_name = full_name
                rec.name = full_name
            else:
                rec.full_name = names[0]

    first_name = fields.Char(string="First Name", size=128)
    third_name = fields.Char(string="Third Name", size=128)
    full_name = fields.Char(string="name", compute="_compute_full_name")
    ar_first_name = fields.Char(string="First Name", size=128)
    ar_middle_name = fields.Char(string="Second Name", size=128)
    ar_third_name = fields.Char(string="Third Name", size=128)
    ar_last_name = fields.Char(string="Last Name", size=128)
    gr_no = fields.Char("Student Number", size=20)

    id_type = fields.Selection(ID_SEL, string="ID type")
    id_file = fields.Binary(string='ID Picture')

    # basic info
    place_of_birth = fields.Char("Place of Birth")
    primary_lang = fields.Selection(LANG_SEL, "Mother Tongue")
    lang_other = fields.Char("Language")
    nationality_id = fields.Many2one("res.country", "Nationality")
    religion = fields.Selection(RELIGION_SEL, "Religion")
    other_religion = fields.Char("Other Religion")

    ## course
    course_id = fields.Many2one("op.course", "Grade")
    batch_id = fields.Many2one("op.batch", "Batch")



