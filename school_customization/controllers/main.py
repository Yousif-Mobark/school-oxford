from datetime import datetime
import base64

from odoo import http
from odoo.http import request

class RegulationHR(http.Controller):

    @http.route('/regulation/hr', type='http', csrf=False, auth="user", website=True)
    def hr_regulation_details(self, **kwargs):
        # user_rec = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
        # if user_rec.has_group('openeducat_core.group_op_student'):
        data = request.env['school.regulation'].search([('regulation_type', '=', 'hr')], limit=1)
        lines_data = request.env['regulation.line'].search([('regulation_id', '=', data.id)], order="sequence asc")
        return request.render('school_customization.hr_regulation_page_template', {'docs': data, 'data_lines': lines_data})

class RegulationAcademic(http.Controller):

    @http.route('/regulation/academic', type='http', csrf=False, auth="user", website=True)
    def regulation_academic_details(self, **kwargs):
        # user_rec = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
        # if user_rec.has_group('openeducat_core.group_op_student'):
        data = request.env['school.regulation'].search([('regulation_type', '=', 'academic')], limit=1)
        lines_data = request.env['regulation.line'].search([('regulation_id', '=', data.id)], order="sequence asc")
        return request.render('school_customization.academic_regulation_page_template', {'docs': data, 'data_lines': lines_data})


class AssignmentOP(http.Controller):

    @http.route('/op/assignment', type='http', csrf=False, auth="user", website=True)
    def assignment_details(self, **kwargs):
        # user_rec = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
        # if user_rec.has_group('openeducat_core.group_op_student'):
        assignments = request.env['op.assignment'].search([('state', 'in', ['publish', 'finish'])])
        user_assignment = []
        user_assignment_answer = {}
        for ass in assignments:
            valid_assigmment = ass.allocation_ids.filtered(lambda l: l.user_id.id == request.env.uid)
            user_answers = ass.assignment_sub_line.mapped('student_id').ids
            if valid_assigmment.id in user_answers:
                user_assignment_answer[ass.id] = True
            if valid_assigmment:
                user_assignment.append(ass)

        return request.render('school_customization.op_assignment_page_template', {'assignments': user_assignment, 'users_answer_list': user_assignment_answer})

class AssignmentAnswer(http.Controller):

    @http.route('/assignment/answer', type='http', csrf=False, auth="user", website=True)
    def answer_assignment_details(self, **kwargs):
        if kwargs:
            assignment_id = kwargs.get('ass_id')
            desc = kwargs.get('desc')
            note = kwargs.get('note')
            assignment_id = request.env['op.assignment'].browse(int(assignment_id))

            if assignment_id:
                student_id = assignment_id.allocation_ids.filtered((lambda l: l.user_id.id == request.env.uid))
                vals = {
                    'student_id': student_id.id,
                    'assignment_id': assignment_id.id,
                    'submission_date': datetime.now(),
                    'description': desc,
                    'note': note,
                }
                assignment_line_id = request.env['op.assignment.sub.line'].create(vals)
                if assignment_line_id:
                    if kwargs.get('file', False):
                        Attachments = request.env['ir.attachment']
                        name = kwargs.get('file').filename
                        file = kwargs.get('file')
                        attachment = file.read()
                        attachment_id = Attachments.sudo().create({
                            'name': name,
                            'datas_fname': name,
                            'res_name': name,
                            'type': 'binary',
                            'res_model': 'op.assignment.sub.line',
                            'res_id': assignment_line_id.id,
                            'datas': base64.encodestring(attachment),
                        })
            return request.render('school_customization.op_assignment_success_page_template', {'message': "Assignment Successfully Pushed"})
        return request.render('school_customization.op_assignment_success_page_template', {'message': "Assignment Submitting Error"})

class AssignmentAnswerSuccess(http.Controller):

    @http.route('/assignment/answer/success', type='http', csrf=False, auth="user", website=True)
    def answer_assignment_success_details(self, **kwargs):
        return request.render('school_customization.op_assignment_success_page_template', {'message': "Assignment Successfully Pushed"})