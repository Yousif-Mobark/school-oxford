from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SchoolYear(models.Model):
    _name = "school.year"
    _description = "School Year"

    STATE_SEL = [
        ('draft', 'New'),
        ('running', 'Running'),
        ('close', 'Closed')
    ]

    @api.multi
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.read(['start_date', 'end_date'])
        return [(year.id, '%s%s' % (year.start_date.year and '%s-' % year.end_date.year or '', year.start_date.year))
                for year in self]

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    fees_ids = fields.One2many("school.fees", "year_id")
    state = fields.Selection(STATE_SEL, default="draft")

    def get_default_year(self):
        default_year = self.search([('state', '=', 'running')], limit=1)
        return default_year.id

    def action_run(self):
        running_years = self.search_count([('state', '=', 'running')])

        for rec in self:
            if running_years > 0:
                raise ValidationError("There is already an open school year")
            else:
                rec.state = 'running'

    def action_close(self):
        for rec in self:
            # TODO: maybe make a confirm wizard
            rec.state = 'close'
