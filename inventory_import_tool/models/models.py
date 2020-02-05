# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import xlrd
from io import BytesIO
import base64


class inventory_import_tool(models.Model):
    _inherit = 'stock.inventory'

    def fill_stock_inventory(self, product, qty):
        pass


class wizard_csv(models.TransientModel):
    _name="stock.inventory.file"

    file = fields.Binary()


    def fill(self):
        if not self.file:
            raise UserError("You should Pick the file!!")
        wb=xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        sheet=wb.sheet_by_index(0)
        valuation=self.env['stock.inventory'].browse(self._context.get("active_id"))
        print(valuation)
        product = self.env['product.product']
        nrows=sheet.nrows
        for i in range(1,nrows):
            row=sheet.row_values(i)
            product_id=self.env.ref(row[0])
            qty=row[1]
            valuation.line_ids.create({
                'location_id':valuation.location_id.id,
                'product_id':product_id.id,
                'product_uom_id':product_id.uom_id.id,
                'product_qty':qty,
                'inventory_id':valuation.id
            })
