# -*- coding: utf-8 -*-
###########
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from openerp.exceptions import Warning as UserError
from io import BytesIO


class rule(models.Model):
    _inherit ='hr.salary.rule'
    _order = "sequence"

class wizardProductMovements(models.Model):
    _name = 'wizard.payslip.report'
    _description = 'print employees details'

    struct_id = fields.Many2one('hr.payroll.structure', 'Structure')
    payslip_ids = fields.Many2many('hr.payslip', 'payslips')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    flag = 1


    @api.onchange('struct_id', 'from_date', 'to_date')
    def onchange_options(self):
        if self.struct_id:
            ids = self.env['hr.payslip'].search(
                [('struct_id', '=', self.struct_id.id), ('date_from', '>=', self.from_date),
                 ('date_to', '<=', self.to_date), ('state', '=', 'done')]).mapped('id')
        else:
            ids = self.env['hr.payslip'].search(
                [('date_from', '>=', self.from_date), ('date_to', '<=', self.to_date), ('state', '=', 'done')]).mapped(
                'id')
        return {'domain': {'payslip_ids': [('id', '=', ids)]}}

    @api.multi
    def print_report(self):
        for report in self:
            # logo = report.env.user.company_id.logo
            from_date = report.from_date
            to_date = report.to_date
            if report.from_date > report.to_date:
                raise UserError(_("You must be enter start date less than end date !"))
            report_title = ' Payslips From ' + str(from_date) + ' to ' + str(to_date)
            file_name = _('  Payslips Report.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Payslips')
            # image_data = BytesIO(base64.b64decode(logo))  # to convert it to base64 file
            # excel_sheet.insert_image('B1', 'logo.png', {'image_data': image_data})
            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': '#8B4789', 'border': 1})
            header_format_sequence = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white'})
            header_format.set_align('center')
            header_format.set_align('vertical center')
            header_format.set_text_wrap()
            format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10'})
            format.set_num_format('#,##0.00')
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format.set_align('center')
            format.set_align('center')
            header_format_sequence.set_align('center')
            format.set_text_wrap()
            format_details = workbook.add_format()
            sequence_format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            sequence_format.set_align('center')
            sequence_format.set_text_wrap()
            total_format = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': '#808080', 'border': 1, 'font_size': '10'})
            total_format.set_align('center')
            total_format.set_text_wrap()
            format_details.set_num_format('#,##0.00')
            col = 0
            row = 7
            excel_sheet.merge_range(0, 1, 5, 5, report_title, title_format)
            excel_sheet.set_column(col, col, 9)
            if self.payslip_ids:
                Total_nets={}
                struct_ids = self.get_structs()
                x=1
                for struct, payslip_ids in struct_ids.items():
                   # row += 3
                    total=0
                   # excel_sheet.merge_range(row, 0, row, 4, struct.name, title_format)
                  #  row += 2

                    if x==1:
                        x=0
                        table_header = self.set_table_Colomn(struct, row, excel_sheet, header_format)

                    for rec in payslip_ids:
                        row += 1
                        excel_sheet.write(row, col, rec.employee_id.name, format)
                        excel_sheet.write(row, col+1, rec.employee_id.bank_account_id.acc_number, format)
                        for line in rec.line_ids:
                            if line.salary_rule_id.code == 'NET':
                                total += line.amount
                            if table_header.get(line.salary_rule_id.id):

                                col1 = table_header[line.salary_rule_id.id]['col']
                            else:
                                col1 = False
                            if col1!=0 and line.salary_rule_id.code == 'NET':
                                excel_sheet.write(row, col1, line.amount, format)
                    Total_nets[struct.name] = total
                   # row+=2
                for r in Total_nets:
                   # excel_sheet.merge_range(row, 0, row, 4, r, header_format)
                    excel_sheet.write(row, 5, Total_nets[r], format)
                   # row+=1


            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['product.movements.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'product.movements.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }


    def set_table_Colomn(self, structure, row, excel_sheet, header_format):
        col = 0
        rule_allocation = {}
        excel_sheet.set_column(col, col, 24)

        excel_sheet.write(row, col, 'Employee Name', header_format)
        col += 1
        excel_sheet.write(row, col, 'Bank Account', header_format)
        col += 1
       # global flag
       # flag += 1

        struct_rules = structure.rule_ids + structure.parent_id.rule_ids
        for rule in struct_rules:
            if  rule.code == 'NET':
                excel_sheet.set_column(col, col, 20)
                excel_sheet.write(row, col, rule.name, header_format)
                rule_allocation[rule.id] = {'col': col, 'row': row}
                col += 1

        return rule_allocation

    def get_structs(self):
        structs = {}
        for payslip in self.payslip_ids:
            if structs.get(payslip.struct_id):
                structs[payslip.struct_id].append(payslip)
            else:
                if payslip.struct_id:
                    structs[payslip.struct_id] = [payslip]
        return structs


class PayslipMonthReportExcel(models.Model):
    _name = 'product.movements.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)


