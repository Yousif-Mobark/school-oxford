
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fees_ok = fields.Boolean('School Fees', default=False)

###########################################################


class ProductProduct(models.Model):
    _inherit = "product.product"

    fees_ok = fields.Boolean('School Fees', default=False)