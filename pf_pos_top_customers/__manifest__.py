{
    'name': 'POS Top Customers & Sales Analytics',
    'version': '15.0.1.0.0',
    'category': 'Point of Sale',
    'sequence': 10,
    'license': 'OPL-1',
    'summary': 'POS Top Customers & Sales Analytics',
    'description': """
       POS Top Customers is a smart and advanced Odoo POS reporting application designed to identify and analyze top-performing customers based on POS sales data. The module helps businesses generate customer ranking reports using filters like From Date, To Date, Minimum POS Amount, Company, and POS Configuration. It automatically calculates customer purchase totals and displays customers with the highest purchase amounts during the selected period. Users can define the number of top customers to display in the report according to business needs. The application also includes a Compare Report feature that helps compare customer purchase performance between two different periods for better sales analysis and customer trend tracking. The module supports multi-company functionality and works with selected POS configurations for accurate reporting. User-wise access control is also available to manage report visibility securely. Additionally, reports can be exported in PDF and XLS formats for easy printing, sharing, and business record management.
    """,
    'author': 'Prefortune Technologies LLP',
    'website': 'https://www.prefortune.com/',
    'maintainer': 'Prefortune Technologies LLP',
    'support': 'odoo@prefortune.com',
    'currency': 'EUR',
    'price': '0.00',
    'depends': ['point_of_sale', 'web'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizard/pos_top_customers_wizard_views.xml',
        'report/pos_top_customers_report_views.xml',
    ],
    'images': ["static/description/banner.png"],
    'installable': True,
    'application': False,
    'auto_install': False,
}
