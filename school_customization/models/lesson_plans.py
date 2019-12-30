from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BookChapter(models.Model):
    _name = "book.chapter"
    order = "number"

    name = fields.Char("Chapter")
    number = fields.Char("Number")
    content = fields.Text("Content")
    book_id = fields.Many2one("book.book", string="Book")

######################################################


class BookBook(models.Model):
    _name = "book.book"

    name = fields.Char("Name")
    subject = fields.Many2one("op.subject")
    course_id = fields.Many2one("op.course", "Grade")
    chapter_ids = fields.One2many("book.chapter", "book_id", string="Chapters")


# ######################################### YEAR #######################################################################


class LessonPlanLine(models.Model):
    _name = "year.plan.line"

    @api.multi
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.read(['chapter_id', 'month'])
        return [(template.id, '%s%s' % (template.chapter_id.name and '[%s] ' % template.month or '', template.chapter_id.name))
                for template in self]

    MONTH_SEL = [
        ('1', "January"),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]

    # onchange functions
    @api.onchange("book_id")
    def onchange_book(self):
        book = self.plan_id.book_id
        if book:
            if book.chapter_ids:
                chapters = book.chapter_ids
                chapter_ids = chapters.ids
            return {'domain': {'chapter_id': [('id', 'in', chapter_ids)]}}
                # for chapter in chapters:
                #     vals = {
                #         'chapter_id': chapter.id,
                #     }
                #     lines.append(vals)
                # self.lines = lines

    month = fields.Selection(MONTH_SEL, "Month")
    plan_id = fields.Many2one("year.plan", "Plan")
    book_id = fields.Many2one("book.book", related="plan_id.book_id")
    chapter_id = fields.Many2one("book.chapter")
    due_date = fields.Date("Finish Date")
    topics = fields.Text("Topics")

########################################################


class LessonPlanYearly(models.Model):
    _name = "year.plan"
    _rec_name = "book_id"

    STATE_SEL = [
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('approve', 'Approve')
    ]

    @api.onchange("course_id", "faculty_id")
    def onchange_faculty_id(self):
        faculty = self.faculty_id
        if self.course_id:
            subject_ids = self.env['op.course'].search([
                ('id', '=', self.course_id.id)]).subject_ids

            subject_ids = subject_ids.filtered(lambda x: x in faculty.faculty_subject_ids)
            return {'domain': {'subject_id': [('id', 'in', subject_ids.ids)]}}

    faculty_id = fields.Many2one(
        'op.faculty', 'Faculty', default=lambda self: self.env[
            'op.faculty'].search([('user_id', '=', self.env.uid)]),
        required=True)

    course_id = fields.Many2one("op.course", "Grade", required=True)
    subject_id = fields.Many2one("op.subject", required=True)
    state = fields.Selection(STATE_SEL, default="draft")
    book_id = fields.Many2one("book.book", "Textbook")
    lines = fields.One2many("year.plan.line", "plan_id", "Lines")
    year_id = fields.Many2one("school.year", "School year",
                              default= lambda self: self.env['school.year'].get_default_year())

    _sql_constraints = [
        ('book_year_uniq', 'unique (book_id)', "This Book Already has a year plan"),
    ]

# Workflow
    def action_submit(self):
        for rec in self:
            emp_id = rec.faculty_id.emp_id
            if not emp_id:
                raise ValidationError(
                    "There is no Employee record attached to your faculty position please contact the system admin")
            if not emp_id.parent_id and (emp_id != emp_id.department_id.manager_id):
                raise ValidationError("there is no specified coordinator to you, please contact HR")
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            current_user = self.env.user
            current_faculty = self.env["op.faculty"].search([('user_id', '=', current_user.id)], limit=1)
            current_emp_id = current_faculty.emp_id
            faculty = rec.faculty_id
            employee = faculty.emp_id
            if current_emp_id != employee.parent_id:
                raise ValidationError(
                    "You're not the coordinator for this faculty member")
            rec.state = 'approve'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'

# ################################################ MONTH ###############################################################


class MonthPlanLine(models.Model):
    _name = "month.plan.line"

    STATE_SEL = [
        ('not_done', 'Not Done'),
        ('partially', 'Partially Done'),
        ('done', 'Done')
    ]
    WEEK_SEL = [
        ('1', "First Week"),
        ('2', 'Second Week'),
        ('3', 'Third Week'),
        ('4', 'Fourth Week'),
        ('5', 'Fifth Week'),
        ]

    plan_id = fields.Many2one("month.plan", "Monthly Plan")
    week = fields.Selection(WEEK_SEL, "Week")
    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    state = fields.Selection(STATE_SEL, default="not_done")
    actual_finish_date = fields.Date("Actual Finish Date")
    reason = fields.Char("Delay Reason")
    # education
    topic = fields.Text("Topic")
    material = fields.Text("Reinforcing material")
    vocabulary = fields.Text("Vocabulary, Terminology and phrases")
    objectives = fields.Text("Learning objective(s)")
    outcome = fields.Text("Lesson outcome")
    work = fields.Text("Class Work")
    homework = fields.Text("Homework")
    comment = fields.Text("Comment")




    # year_plan_id = fields.Many2one("year.plan", related="plan_id.year_plan_id")

    def check_user(self):
        current_user = self.env.user
        current_faculty = self.env["op.faculty"].search([('user_id', '=', current_user.id)], limit=1)
        current_emp_id = current_faculty.emp_id
        faculty = self.plan_id.faculty_id
        employee = faculty.emp_id
        if current_emp_id != employee.parent_id:
            raise ValidationError(
                "You're not the coordinator for this faculty member")

    def action_partially_done(self):
        for rec in self:
            self.check_user()
            rec.state = 'partially'

    def action_done(self):
        for rec in self:
            self.check_user()
            rec.state = 'done'

    def open_line(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Model Title',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': id[0],
            'target': 'current',
        }

#########################################################


class LessonPlanMonth(models.Model):
    _name = "month.plan"

    STATE_SEL = [
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('approve', 'Approve')
    ]

    @api.onchange("faculty_id")
    def onchange_faculty_id(self):
        faculty = self.faculty_id
        if faculty:
            year_plans = self.env["year.plan"].search([('faculty_id', '=', faculty.id)])
            if year_plans:
                return {'domain': {'year_plan_id': [('id', 'in', year_plans.ids)]}}

    @api.onchange("year_plan_id")
    def onchange_year_plan(self):
        year_plan = self.year_plan_id
        year_plan_line_id = False
        if year_plan:
            year_plan_lines = year_plan.lines
            if year_plan_lines:
                return {'domain': {'year_plan_line_id': [('id', 'in', year_plan_lines.ids)]}}

    faculty_id = fields.Many2one(
        'op.faculty', 'Faculty', default=lambda self: self.env[
            'op.faculty'].search([('user_id', '=', self.env.uid)]),
        required=True)
    # month of what year
    year_plan_id = fields.Many2one("year.plan", required=True)
    year_plan_line_id = fields.Many2one("year.plan.line", "Month to Plan")

    book_id = fields.Many2one("book.book", related="year_plan_id.book_id")
    course_id = fields.Many2one("op.course", related="year_plan_id.course_id")
    subject_id = fields.Many2one("op.subject", related="year_plan_id.subject_id")

    from_date = fields.Date("From Date",  required=True)
    to_date = fields.Date("To Date",  required=True)

    lines = fields.One2many("month.plan.line", "plan_id", "Lines")
    state = fields.Selection(STATE_SEL, default="draft")

    def action_submit(self):
        for rec in self:
            emp_id = rec.faculty_id.emp_id
            if not emp_id:
                raise ValidationError(
                    "There is no Employee record attached to your faculty position please contact the system admin")
            if not emp_id.parent_id:
                raise ValidationError("there is no specified coordinator to you, please contact HR")
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            current_user = self.env.user
            current_faculty = self.env["op.faculty"].search([('user_id', '=', current_user.id)], limit=1)
            current_emp_id = current_faculty.emp_id
            faculty = rec.faculty_id
            employee = faculty.emp_id
            if current_emp_id != employee.parent_id:
                raise ValidationError(
                    "You're not the coordinator for this faculty member")
            rec.state = 'approve'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'
