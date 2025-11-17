"""
Admin Dashboard with Sales Statistics and Charts
"""
from django.shortcuts import render
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Sale, SaleItem, Product


class AdminDashboard:
    """Dashboard with sales statistics"""
    
    def __init__(self, admin_site=None):
        self.admin_site = admin_site
    
    def get_dashboard_context(self, request):
        """Get all dashboard statistics"""
        today = timezone.now().date()
        
        # Date ranges
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        
        context = {
            'today_stats': self.get_daily_stats(today),
            'week_stats': self.get_period_stats(week_start, today),
            'month_stats': self.get_period_stats(month_start, today),
            'year_stats': self.get_period_stats(year_start, today),
            'top_products_week': self.get_top_products(week_start, today),
            'top_products_month': self.get_top_products(month_start, today),
            'daily_sales_chart': self.get_daily_sales_data(30),  # Last 30 days
            'weekly_sales_chart': self.get_weekly_sales_data(12),  # Last 12 weeks
            'monthly_revenue_chart': self.get_monthly_revenue_data(12),  # Last 12 months
            'category_distribution': self.get_category_distribution(),
        }
        
        return context
    
    def get_daily_stats(self, date):
        """Get statistics for a specific day"""
        sales = Sale.objects.filter(
            created_at__date=date,
            status='COMPLETED'
        )
        
        stats = sales.aggregate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            avg_ticket=Avg('total_amount'),
            total_items=Sum('items__quantity')
        )
        
        return {
            'total_sales': stats['total_sales'] or 0,
            'total_revenue': stats['total_revenue'] or Decimal('0.00'),
            'avg_ticket': stats['avg_ticket'] or Decimal('0.00'),
            'total_items': stats['total_items'] or 0,
        }
    
    def get_period_stats(self, start_date, end_date):
        """Get statistics for a date range"""
        sales = Sale.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='COMPLETED'
        )
        
        stats = sales.aggregate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            avg_ticket=Avg('total_amount'),
            total_items=Sum('items__quantity'),
            total_discount=Sum('discount')
        )
        
        # Calculate profit (simplified - revenue minus costs)
        items = SaleItem.objects.filter(
            sale__in=sales
        ).select_related('product')
        
        total_cost = sum(
            item.quantity * (item.product.cost_price or Decimal('0'))
            for item in items
        )
        
        revenue = stats['total_revenue'] or Decimal('0.00')
        profit = revenue - Decimal(str(total_cost))
        
        return {
            'total_sales': stats['total_sales'] or 0,
            'total_revenue': revenue,
            'total_profit': profit,
            'profit_margin': (profit / revenue * 100) if revenue > 0 else Decimal('0.00'),
            'avg_ticket': stats['avg_ticket'] or Decimal('0.00'),
            'total_items': stats['total_items'] or 0,
            'total_discount': stats['total_discount'] or Decimal('0.00'),
        }
    
    def get_top_products(self, start_date, end_date, limit=10):
        """Get top selling products for period"""
        top_products = SaleItem.objects.filter(
            sale__created_at__date__gte=start_date,
            sale__created_at__date__lte=end_date,
            sale__status='COMPLETED'
        ).values(
            'product__name',
            'product__code'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price')),
            times_sold=Count('sale', distinct=True)
        ).order_by('-total_quantity')[:limit]
        
        return list(top_products)
    
    def get_daily_sales_data(self, days=30):
        """Get daily sales data for chart"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        daily_data = Sale.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='COMPLETED'
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            sales=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('date')
        
        return {
            'labels': [item['date'].strftime('%d/%m') for item in daily_data],
            'sales': [item['sales'] for item in daily_data],
            'revenue': [float(item['revenue']) for item in daily_data],
        }
    
    def get_weekly_sales_data(self, weeks=12):
        """Get weekly sales data for chart"""
        end_date = timezone.now()
        start_date = end_date - timedelta(weeks=weeks)
        
        weekly_data = Sale.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            status='COMPLETED'
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            sales=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('week')
        
        return {
            'labels': [item['week'].strftime('%d/%m') for item in weekly_data],
            'sales': [item['sales'] for item in weekly_data],
            'revenue': [float(item['revenue']) for item in weekly_data],
        }
    
    def get_monthly_revenue_data(self, months=12):
        """Get monthly revenue data for chart"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=months*30)
        
        monthly_data = Sale.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            status='COMPLETED'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            sales=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('month')
        
        return {
            'labels': [item['month'].strftime('%b/%Y') for item in monthly_data],
            'sales': [item['sales'] for item in monthly_data],
            'revenue': [float(item['revenue']) for item in monthly_data],
        }
    
    def get_category_distribution(self):
        """Get sales distribution by category"""
        category_data = SaleItem.objects.filter(
            sale__status='COMPLETED'
        ).values(
            'product__category__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-total_revenue')[:10]
        
        return {
            'labels': [item['product__category__name'] or 'Sem Categoria' for item in category_data],
            'quantities': [item['total_quantity'] for item in category_data],
            'revenues': [float(item['total_revenue']) for item in category_data],
        }
    
    def dashboard_view(self, request):
        """Main dashboard view"""
        context = self.get_dashboard_context(request)
        
        # Add admin context if admin_site is available
        if self.admin_site:
            context.update(self.admin_site.each_context(request))
        
        context.update({
            'site_title': 'M007 System - Dashboard',
            'site_header': 'Dashboard de Vendas',
            'has_permission': True,
        })
        
        return render(request, 'admin/dashboard.html', context)
