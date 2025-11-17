"""
Advanced Admin Reports with PDF Generation
"""
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from datetime import datetime, timedelta
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .models import Sale, Product, Customer, WeeklySalesReport, SellerPerformance


class SalesReportAdmin:
    """
    Custom Admin View for Sales Reports
    """
    
    def __init__(self, admin_site=None):
        self.admin_site = admin_site
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('sales-reports/', self.admin_site.admin_view(self.sales_reports_view), name='sales_reports'),
            path('sales-reports/pdf/', self.admin_site.admin_view(self.generate_pdf_report), name='sales_reports_pdf'),
        ]
        return custom_urls + urls
    
    def sales_reports_view(self, request):
        """
        Main sales reports dashboard
        """
        # Get filter parameters
        report_type = request.GET.get('type', 'daily')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        seller_id = request.GET.get('seller')
        
        # Base queryset
        sales_qs = Sale.objects.filter(status='COMPLETED')
        
        # Apply date filters
        if start_date:
            sales_qs = sales_qs.filter(created_at__gte=start_date)
        if end_date:
            sales_qs = sales_qs.filter(created_at__lte=end_date)
        if seller_id:
            sales_qs = sales_qs.filter(seller_id=seller_id)
        
        # Generate report based on type
        if report_type == 'daily':
            report_data = self.get_daily_report(sales_qs, start_date, end_date)
        elif report_type == 'weekly':
            report_data = self.get_weekly_report(sales_qs)
        elif report_type == 'monthly':
            report_data = self.get_monthly_report(sales_qs)
        elif report_type == 'yearly':
            report_data = self.get_yearly_report(sales_qs)
        else:
            report_data = self.get_daily_report(sales_qs, start_date, end_date)
        
        # Get sellers for filter
        from django.contrib.auth.models import User
        sellers = User.objects.filter(profile__role__in=['SELLER', 'MANAGER', 'ADMIN'])
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Relatórios de Vendas',
            'report_type': report_type,
            'report_data': report_data,
            'sellers': sellers,
            'start_date': start_date,
            'end_date': end_date,
            'seller_id': seller_id,
        }
        
        return render(request, 'admin/sales_reports.html', context)
    
    def get_daily_report(self, sales_qs, start_date=None, end_date=None):
        """Generate daily sales report"""
        if not start_date:
            start_date = timezone.now().date() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
        
        daily_sales = sales_qs.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            total_items=Sum('items__quantity'),
            avg_sale_value=Avg('total_amount')
        ).order_by('-date')
        
        return {
            'type': 'Diário',
            'period': f'{start_date} até {end_date}',
            'data': list(daily_sales),
            'summary': {
                'total_sales': sales_qs.count(),
                'total_revenue': sales_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
                'avg_sale': sales_qs.aggregate(Avg('total_amount'))['total_amount__avg'] or 0,
            }
        }
    
    def get_weekly_report(self, sales_qs):
        """Generate weekly sales report"""
        weekly_sales = sales_qs.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            total_items=Sum('items__quantity'),
            avg_sale_value=Avg('total_amount')
        ).order_by('-week')[:12]  # Last 12 weeks
        
        return {
            'type': 'Semanal',
            'period': 'Últimas 12 semanas',
            'data': list(weekly_sales),
            'summary': {
                'total_sales': sales_qs.count(),
                'total_revenue': sales_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
                'avg_sale': sales_qs.aggregate(Avg('total_amount'))['total_amount__avg'] or 0,
            }
        }
    
    def get_monthly_report(self, sales_qs):
        """Generate monthly sales report"""
        monthly_sales = sales_qs.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            total_items=Sum('items__quantity'),
            avg_sale_value=Avg('total_amount')
        ).order_by('-month')[:12]  # Last 12 months
        
        return {
            'type': 'Mensal',
            'period': 'Últimos 12 meses',
            'data': list(monthly_sales),
            'summary': {
                'total_sales': sales_qs.count(),
                'total_revenue': sales_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
                'avg_sale': sales_qs.aggregate(Avg('total_amount'))['total_amount__avg'] or 0,
            }
        }
    
    def get_yearly_report(self, sales_qs):
        """Generate yearly sales report"""
        yearly_sales = sales_qs.annotate(
            year=TruncYear('created_at')
        ).values('year').annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            total_items=Sum('items__quantity'),
            avg_sale_value=Avg('total_amount')
        ).order_by('-year')
        
        return {
            'type': 'Anual',
            'period': 'Todos os anos',
            'data': list(yearly_sales),
            'summary': {
                'total_sales': sales_qs.count(),
                'total_revenue': sales_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
                'avg_sale': sales_qs.aggregate(Avg('total_amount'))['total_amount__avg'] or 0,
            }
        }
    
    def generate_pdf_report(self, request):
        """
        Generate PDF report
        """
        report_type = request.GET.get('type', 'daily')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Create HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="relatorio_vendas_{report_type}_{timezone.now().strftime("%Y%m%d")}.pdf"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=12,
        )
        
        # Title
        title = Paragraph("PDV System - Relatório de Vendas", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report info
        info_text = f"""
        <para align=center>
        <b>Tipo de Relatório:</b> {report_type.title()}<br/>
        <b>Data de Geração:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}<br/>
        </para>
        """
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Get data
        sales_qs = Sale.objects.filter(status='COMPLETED')
        if start_date:
            sales_qs = sales_qs.filter(created_at__gte=start_date)
        if end_date:
            sales_qs = sales_qs.filter(created_at__lte=end_date)
        
        if report_type == 'daily':
            report_data = self.get_daily_report(sales_qs, start_date, end_date)
        elif report_type == 'weekly':
            report_data = self.get_weekly_report(sales_qs)
        elif report_type == 'monthly':
            report_data = self.get_monthly_report(sales_qs)
        else:
            report_data = self.get_yearly_report(sales_qs)
        
        # Summary section
        summary = report_data['summary']
        summary_heading = Paragraph("Resumo Geral", heading_style)
        story.append(summary_heading)
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Vendas', f"{summary['total_sales']}"],
            ['Receita Total', f"{summary['total_revenue']:,.2f} Kz"],
            ['Valor Médio por Venda', f"{summary['avg_sale']:,.2f} Kz"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Detailed data
        detail_heading = Paragraph("Detalhamento", heading_style)
        story.append(detail_heading)
        
        # Prepare table data
        table_data = [['Período', 'Vendas', 'Receita', 'Ticket Médio']]
        
        for item in report_data['data'][:20]:  # Limit to 20 rows
            period_key = list(item.keys())[0]
            period_value = item[period_key]
            if isinstance(period_value, datetime):
                period_str = period_value.strftime('%d/%m/%Y')
            else:
                period_str = str(period_value)
            
            table_data.append([
                period_str,
                str(item['total_sales']),
                f"{item['total_revenue']:,.2f} Kz",
                f"{item['avg_sale_value']:,.2f} Kz"
            ])
        
        detail_table = Table(table_data, colWidths=[2*inch, 1.5*inch, 2*inch, 2*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
        ]))
        
        story.append(detail_table)
        
        # Build PDF
        doc.build(story)
        
        return response
