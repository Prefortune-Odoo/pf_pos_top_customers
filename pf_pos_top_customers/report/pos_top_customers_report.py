from odoo import models, api

class POSReportTopCustomers(models.AbstractModel):
    _name = 'report.pf_pos_top_customers.report_top_customers_template'
    _description = 'Top POS Customers QWeb Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pf.pos.top.customers.wizard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'pf.pos.top.customers.wizard',
            'docs': docs,
            'data': data,
            'get_report_data': lambda doc: doc.get_report_data(),
        }
