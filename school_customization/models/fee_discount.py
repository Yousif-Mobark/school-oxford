from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FeeDiscount(models.Model):
    _name = "fee.discount"

    TYPE_SEL = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ]

    name = fields.Char(string="Name", required=True)
    # state = fields.Selection()
    type = fields.Selection(TYPE_SEL, string="Type", default="percentage")
    percentage = fields.Float(string="Percentage")
    amount = fields.Float(string="Amount")
    active = fields.Boolean(string="Active", default=True)




