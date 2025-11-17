"""
Custom Admin Site with Reports
"""
from django.contrib import admin
from django.urls import path

__all__ = ['pdv_admin_site']


class PDVAdminSite(admin.AdminSite):
    site_header = "M007 System - Painel Administrativo"
    site_title = "M007 Admin"
    index_title = "Bem-vindo ao Painel de Gestão"
    
    def get_urls(self):
        from .admin_reports import SalesReportAdmin
        from .admin_dashboard import AdminDashboard
        
        urls = super().get_urls()
        
        # Instantiate with admin_site reference
        sales_report_admin = SalesReportAdmin(admin_site=self)
        dashboard_admin = AdminDashboard(admin_site=self)
        
        custom_urls = [
            path('dashboard/', self.admin_view(dashboard_admin.dashboard_view), name='dashboard'),
            path('sales-reports/', self.admin_view(sales_report_admin.sales_reports_view), name='sales_reports'),
            path('sales-reports/pdf/', self.admin_view(sales_report_admin.generate_pdf_report), name='sales_reports_pdf'),
        ]
        return custom_urls + urls


# Create custom admin site instance
pdv_admin_site = PDVAdminSite(name='m007_admin')