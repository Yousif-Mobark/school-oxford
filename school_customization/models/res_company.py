from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo.exceptions import ValidationError, UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    transport_product_id = fields.Many2one("product.product", domain=[('type', '=', 'service')])
    registration_product_id = fields.Many2one("product.product", domain=[('type', '=', 'service')])


###################################################################################################

