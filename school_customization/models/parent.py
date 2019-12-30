from odoo import models, fields, api, _
from odoo.exceptions import Warning


class OpParent(models.Model):
    _inherit = "op.parent"

    country_id = fields.Many2one("res.country", related='name.country_id', readonly=False)
    occupation = fields.Char("occupation")
    address = fields.Text("Address")
    email = fields.Char("Email", related='name.email', readonly=False)
    mobile = fields.Char(string='Mobile', related='name.mobile', readonly=False)
