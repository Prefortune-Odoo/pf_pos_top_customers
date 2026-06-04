from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    enable_pos_top_customer_report_access = fields.Boolean(
        string='Enable POS Top Customer Report Access',
        compute='_compute_enable_pos_top_customer_report_access',
        inverse='_inverse_enable_pos_top_customer_report_access',
    )

    @api.depends('group_ids')
    def _compute_enable_pos_top_customer_report_access(self):
        group = self.env.ref('pf_pos_top_customers.group_top_pos_customers_report', raise_if_not_found=False)
        for user in self:
            if group:
                user.enable_pos_top_customer_report_access = group in user.group_ids
            else:
                user.enable_pos_top_customer_report_access = False

    def _inverse_enable_pos_top_customer_report_access(self):
        group = self.env.ref('pf_pos_top_customers.group_top_pos_customers_report', raise_if_not_found=False)
        if not group:
            return
        for user in self:
            if user.enable_pos_top_customer_report_access:
                user.write({'group_ids': [(4, group.id)]})
            else:
                user.write({'group_ids': [(3, group.id)]})
