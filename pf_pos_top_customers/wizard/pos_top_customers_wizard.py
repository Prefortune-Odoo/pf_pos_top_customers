from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class POSTopCustomersWizard(models.TransientModel):
    _name = 'pf.pos.top.customers.wizard'
    _description = 'POS Top Customers Wizard'

    report_type = fields.Selection([
        ('basic', 'Basic'),
        ('compare', 'Compare')
    ], string='Report Type', default='basic', required=True)

    current_datetime_str = fields.Char(compute='_compute_current_datetime_str')

    def _compute_current_datetime_str(self):
        import pytz
        for record in self:
            user_tz = self.env.user.tz or self.env.context.get('tz') or 'UTC'
            local_tz = pytz.timezone(user_tz)
            local_time = datetime.now(pytz.utc).astimezone(local_tz)
            record.current_datetime_str = local_time.strftime('%Y-%m-%d %H_%M_%S')

    from_date = fields.Datetime(
        string='From Date',
        required=True,
        default=lambda self: fields.Datetime.now() - timedelta(days=30)
    )
    to_date = fields.Datetime(
        string='To Date',
        required=True,
        default=fields.Datetime.now
    )

    comp_from_date = fields.Datetime(string='Compare From Date')
    comp_to_date = fields.Datetime(string='Compare To Date')

    no_of_items = fields.Integer(string='No of Items', default=10, required=True)
    total_pos_amount = fields.Float(string='Minimum POS Amount', default=0.0)

    company_ids = fields.Many2many(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    pos_config_ids = fields.Many2many(
        'pos.config',
        string='POS Configuration'
    )

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        for record in self:
            if record.from_date and record.to_date and record.from_date > record.to_date:
                raise ValidationError(_("From Date cannot be greater than To Date."))

    @api.constrains('comp_from_date', 'comp_to_date')
    def _check_comp_dates(self):
        for record in self:
            if record.report_type == 'compare' and record.comp_from_date and record.comp_to_date:
                if record.comp_from_date > record.comp_to_date:
                    raise ValidationError(_("Compare From Date cannot be greater than Compare To Date."))

    @api.constrains('no_of_items')
    def _check_no_of_items(self):
        for record in self:
            if record.no_of_items <= 0:
                raise ValidationError(_("No of Items must be a positive integer."))

    @api.constrains('total_pos_amount')
    def _check_total_pos_amount(self):
        for record in self:
            if record.total_pos_amount < 0:
                raise ValidationError(_("Minimum POS Amount cannot be negative."))

    def _get_top_customers(self, from_date, to_date):
        self.ensure_one()
        params = [from_date, to_date]
        query = """
            SELECT po.partner_id, COALESCE(rp.name, 'Walk-in Customer') as partner_name, SUM(po.amount_total) as total_amount, COUNT(po.id) as order_count
            FROM pos_order po
            LEFT JOIN res_partner rp ON po.partner_id = rp.id
            WHERE po.date_order >= %s
              AND po.date_order <= %s
              AND po.state NOT IN ('draft', 'cancel')
        """
        
        if self.company_ids:
            query += " AND po.company_id IN %s"
            params.append(tuple(self.company_ids.ids))
            
        if self.pos_config_ids:
            query += " AND po.session_id IN (SELECT id FROM pos_session WHERE config_id IN %s)"
            params.append(tuple(self.pos_config_ids.ids))
            
        query += """
            GROUP BY po.partner_id, rp.name
        """
        if self.total_pos_amount > 0:
            query += " HAVING SUM(po.amount_total) > %s "
            params.append(self.total_pos_amount)
            
        query += """
            ORDER BY total_amount DESC
            LIMIT %s
        """
        params.append(self.no_of_items)
        
        self.env.cr.execute(query, params)
        return self.env.cr.dictfetchall()

    def get_report_data(self):
        self.ensure_one()
        active_data = self._get_top_customers(self.from_date, self.to_date)
        
        if self.report_type == 'basic':
            results = []
            for idx, item in enumerate(active_data, 1):
                results.append({
                    'index': idx,
                    'partner_name': item['partner_name'],
                    'order_count': item['order_count'],
                    'total_amount': item['total_amount']
                })
            return results
        else:
            compare_data = self._get_top_customers(self.comp_from_date, self.comp_to_date)
            compare_partners = {item['partner_id'] for item in compare_data}
            active_partners = {item['partner_id'] for item in active_data}
            
            new_customers = [item['partner_name'] for item in active_data if item['partner_id'] not in compare_partners]
            lost_customers = [item['partner_name'] for item in compare_data if item['partner_id'] not in active_partners]
            
            active_list = [{
                'index': idx,
                'partner_name': item['partner_name'],
                'total_amount': item['total_amount']
            } for idx, item in enumerate(active_data, 1)]
            
            compare_list = [{
                'index': idx,
                'partner_name': item['partner_name'],
                'total_amount': item['total_amount']
            } for idx, item in enumerate(compare_data, 1)]
            
            max_len = max(len(active_list), len(compare_list))
            combined_data = []
            for i in range(max_len):
                combined_data.append({
                    'index': i,
                    'active': active_list[i] if i < len(active_list) else None,
                    'compare': compare_list[i] if i < len(compare_list) else None,
                })

            return {
                'active_data': active_list,
                'compare_data': compare_list,
                'combined_data': combined_data,
                'new_customers': new_customers,
                'lost_customers': lost_customers,
            }

    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref('pf_pos_top_customers.action_report_pos_top_customers').report_action(self)

    def action_print_xls(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/excel_report/top_customers?wizard_id={self.id}',
            'target': 'new',
        }
