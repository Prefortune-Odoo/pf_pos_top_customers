import io
from datetime import datetime
from odoo import http
from odoo.http import request
import xlsxwriter

class TopCustomersXlsxController(http.Controller):

    @http.route('/web/excel_report/top_customers', type='http', auth='user')
    def get_top_customers_excel(self, wizard_id, **kw):
        wizard = request.env['pf.pos.top.customers.wizard'].browse(int(wizard_id))
        if not wizard.exists():
            return request.not_found()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Top Customers')

        # Formats
        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 14,
        })
        info_format = workbook.add_format({
            'font_size': 10,
        })
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'bg_color': '#EFEFEF',
            'border': 1,
            'font_size': 10,
        })
        cell_center_format = workbook.add_format({
            'align': 'center',
            'border': 1,
            'font_size': 10,
        })
        cell_left_format = workbook.add_format({
            'align': 'left',
            'border': 1,
            'font_size': 10,
        })
        cell_right_format = workbook.add_format({
            'align': 'right',
            'border': 1,
            'num_format': '#,##0.00',
            'font_size': 10,
        })
        cell_right_bold_format = workbook.add_format({
            'bold': True,
            'align': 'right',
            'border': 1,
            'num_format': '#,##0.00',
            'font_size': 10,
        })

       
        if wizard.report_type == 'basic':
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 35)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 18)
            
            worksheet.merge_range('A1:D1', 'Top Customers', title_format)
            
          
            from_str = wizard.from_date.strftime('%Y-%m-%d %H:%M:%S') if wizard.from_date else ''
            to_str = wizard.to_date.strftime('%Y-%m-%d %H:%M:%S') if wizard.to_date else ''
            worksheet.write('A3', f'From Date: {from_str}', info_format)
            worksheet.write('A4', f'To Date:   {to_str}', info_format)
            
          
            worksheet.write('A7', '#', header_format)
            worksheet.write('B7', 'Customer', header_format)
            worksheet.write('C7', 'Orders Count', header_format)
            worksheet.write('D7', 'POS Amount', header_format)
            
           
            row_idx = 7
            data = wizard.get_report_data()
            for row in data:
                worksheet.write(row_idx, 0, row['index'], cell_center_format)
                worksheet.write(row_idx, 1, row['partner_name'], cell_left_format)
                worksheet.write(row_idx, 2, row['order_count'], cell_center_format)
                worksheet.write(row_idx, 3, row['total_amount'], cell_right_format)
                row_idx += 1
                

        else:
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 35)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 5)
            worksheet.set_column('E:E', 5)
            worksheet.set_column('F:F', 35)
            worksheet.set_column('G:G', 15)
            
            worksheet.merge_range('A1:G1', 'Top Customers', title_format)
            
            from_str = wizard.from_date.strftime('%Y-%m-%d %H:%M:%S') if wizard.from_date else ''
            to_str = wizard.to_date.strftime('%Y-%m-%d %H:%M:%S') if wizard.to_date else ''
            comp_from_str = wizard.comp_from_date.strftime('%Y-%m-%d %H:%M:%S') if wizard.comp_from_date else ''
            comp_to_str = wizard.comp_to_date.strftime('%Y-%m-%d %H:%M:%S') if wizard.comp_to_date else ''
            
            worksheet.write(2, 0, 'From Date', info_format)
            worksheet.write(2, 1, from_str, info_format)
            worksheet.write(3, 0, 'To Date', info_format)
            worksheet.write(3, 1, to_str, info_format)
            
            worksheet.write(2, 4, 'Compare From Date', info_format)
            worksheet.write(2, 5, comp_from_str, info_format)
            worksheet.write(3, 4, 'Compare To Date', info_format)
            worksheet.write(3, 5, comp_to_str, info_format)
            
           
            worksheet.write('A7', '#', header_format)
            worksheet.write('B7', 'Customer', header_format)
            worksheet.write('C7', 'POS Amount', header_format)
            
            worksheet.write('E7', '#', header_format)
            worksheet.write('F7', 'Compare Customer', header_format)
            worksheet.write('G7', 'POS Amount', header_format)
            
           
            row_idx = 7
            report_data = wizard.get_report_data()
            active_data = report_data['active_data']
            compare_data = report_data['compare_data']
            
            max_len = max(len(active_data), len(compare_data))
            for i in range(max_len):
                if i < len(active_data):
                    item = active_data[i]
                    worksheet.write(row_idx, 0, item['index'], cell_center_format)
                    worksheet.write(row_idx, 1, item['partner_name'], cell_left_format)
                    worksheet.write(row_idx, 2, item['total_amount'], cell_right_format)
                if i < len(compare_data):
                    item = compare_data[i]
                    worksheet.write(row_idx, 4, item['index'], cell_center_format)
                    worksheet.write(row_idx, 5, item['partner_name'], cell_left_format)
                    worksheet.write(row_idx, 6, item['total_amount'], cell_right_format)
                row_idx += 1
                
          
            row_idx += 2
            
            gray_header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'bg_color': '#D3D3D3',
                'border': 1,
                'font_size': 10,
            })
            
            worksheet.merge_range(row_idx, 0, row_idx, 2, 'New Customers', gray_header_format)
            worksheet.merge_range(row_idx, 4, row_idx, 6, 'Lost Customers', gray_header_format)
            row_idx += 1
            
            new_custs = report_data['new_customers']
            lost_custs = report_data['lost_customers']
            max_cust_len = max(len(new_custs), len(lost_custs))
            
            if max_cust_len == 0:
                worksheet.merge_range(row_idx, 0, row_idx, 2, 'No new customers.', cell_center_format)
                worksheet.merge_range(row_idx, 4, row_idx, 6, 'No lost customers.', cell_center_format)
                row_idx += 1
            else:
                for i in range(max_cust_len):
                    if i < len(new_custs):
                        worksheet.merge_range(row_idx, 0, row_idx, 2, new_custs[i], cell_left_format)
                    else:
                        if i == 0:
                            worksheet.merge_range(row_idx, 0, row_idx, 2, 'No new customers.', cell_center_format)
                        else:
                            worksheet.merge_range(row_idx, 0, row_idx, 2, '', cell_center_format)
                            
                    if i < len(lost_custs):
                        worksheet.merge_range(row_idx, 4, row_idx, 6, lost_custs[i], cell_left_format)
                    else:
                        if i == 0:
                            worksheet.merge_range(row_idx, 4, row_idx, 6, 'No lost customers.', cell_center_format)
                        else:
                            worksheet.merge_range(row_idx, 4, row_idx, 6, '', cell_center_format)
                    row_idx += 1

                
        workbook.close()
        output.seek(0)
        
        user_tz = request.env.user.tz or request.env.context.get('tz') or 'UTC'
        import pytz
        local_tz = pytz.timezone(user_tz)
        local_time = datetime.now(pytz.utc).astimezone(local_tz)
        date_str = local_time.strftime('%Y-%m-%d %H_%M_%S')
        file_name = f"Top_POS_Customers - {date_str}.xlsx"
        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename="{file_name}"')
            ]
        )
