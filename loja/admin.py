"""
Django Admin Configuration for PDV System
Customized admin interface with filters, search, and inline editing
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Category, UnitOfMeasure, Product, UserProfile, Customer,
    Order, OrderItem, Sale, SaleItem, WeeklySalesReport,
    SellerPerformance, AuditLog, Notification
)


# ============================================================================
# RESOURCES FOR IMPORT/EXPORT
# ============================================================================

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'code', 'name', 'category__name', 'unit_price', 'stock_quantity', 'minimum_stock')
        export_order = fields


class SaleResource(resources.ModelResource):
    class Meta:
        model = Sale
        fields = ('sale_number', 'seller__username', 'customer__full_name', 'total_amount', 'payment_method', 'created_at')
        export_order = fields


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class OrderItemInline(admin.TabularInline):
    """Inline for Order Items"""
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'total_price', 'notes']
    readonly_fields = ['total_price']
    autocomplete_fields = ['product']


class SaleItemInline(admin.TabularInline):
    """Inline for Sale Items"""
    model = SaleItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'total_price', 'notes']
    readonly_fields = ['total_price']
    autocomplete_fields = ['product']


class SellerPerformanceInline(admin.TabularInline):
    """Inline for Seller Performance in Weekly Reports"""
    model = SellerPerformance
    extra = 0
    fields = ['seller', 'total_sales', 'total_revenue', 'total_items_sold', 'average_sale_value']
    readonly_fields = ['seller', 'total_sales', 'total_revenue', 'total_items_sold', 'average_sale_value']
    can_delete = False


# ============================================================================
# MODEL ADMIN CLASSES
# ============================================================================

class CategoryAdmin(admin.ModelAdmin):
    """Admin for Categories"""
    list_display = ['name', 'product_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        """Display number of products in category"""
        count = obj.products.filter(is_active=True).count()
        return format_html('<b>{}</b> produtos', count)
    product_count.short_description = 'Produtos'


class UnitOfMeasureAdmin(admin.ModelAdmin):
    """Admin for Units of Measure"""
    list_display = ['name', 'abbreviation', 'unit_type', 'base_unit_conversion', 'allows_fraction', 'is_active']
    list_filter = ['unit_type', 'allows_fraction', 'is_active']
    search_fields = ['name', 'abbreviation']
    list_per_page = 25
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'abbreviation', 'unit_type')
        }),
        ('Configurações', {
            'fields': ('base_unit_conversion', 'allows_fraction', 'is_active')
        }),
    )


class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """Admin for Products"""
    resource_class = ProductResource
    list_display = ['code', 'name', 'category', 'unit_price', 'stock_badge', 'stock_quantity', 'is_active']
    list_filter = ['category', 'stock_status', 'is_active', 'unit_of_measure', 'created_at']
    search_fields = ['code', 'name', 'barcode', 'description']
    readonly_fields = ['stock_status', 'created_at', 'updated_at', 'product_image_preview']
    list_editable = ['unit_price', 'is_active']
    list_per_page = 25
    autocomplete_fields = ['category']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('code', 'name', 'description', 'category', 'barcode')
        }),
        ('Preços', {
            'fields': ('unit_price', 'cost_price', 'unit_of_measure')
        }),
        ('Estoque', {
            'fields': ('stock_quantity', 'minimum_stock', 'stock_status', 'allows_bulk_sale')
        }),
        ('Imagem', {
            'fields': ('image', 'product_image_preview'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_badge(self, obj):
        """Display stock status with colored badge"""
        colors = {
            'IN_STOCK': '#28a745',
            'LOW_STOCK': '#ffc107',
            'OUT_OF_STOCK': '#dc3545'
        }
        color = colors.get(obj.stock_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_stock_status_display()
        )
    stock_badge.short_description = 'Status do Estoque'
    
    def product_image_preview(self, obj):
        """Display product image preview"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        return "Sem imagem"
    product_image_preview.short_description = 'Preview da Imagem'
    
    actions = ['update_stock_status']
    
    def update_stock_status(self, request, queryset):
        """Action to update stock status for selected products"""
        for product in queryset:
            product.update_stock_status()
        self.message_user(request, f'{queryset.count()} produtos atualizados.')
    update_stock_status.short_description = 'Atualizar status do estoque'


class UserProfileAdmin(admin.ModelAdmin):
    """Admin for User Profiles"""
    list_display = ['user', 'role', 'phone', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'cpf', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'avatar_preview']
    list_per_page = 25
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'role')
        }),
        ('Informações Pessoais', {
            'fields': ('cpf', 'phone', 'address', 'birth_date')
        }),
        ('Avatar', {
            'fields': ('avatar', 'avatar_preview'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def avatar_preview(self, obj):
        """Display avatar preview"""
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 50%;" />', obj.avatar.url)
        return "Sem avatar"
    avatar_preview.short_description = 'Preview do Avatar'


class CustomerAdmin(admin.ModelAdmin):
    """Admin for Customers"""
    list_display = ['full_name', 'phone', 'email', 'total_purchases_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'cpf']
    readonly_fields = ['created_at', 'updated_at', 'total_purchases_display']
    list_per_page = 25
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Endereço e Documentos', {
            'fields': ('address', 'cpf')
        }),
        ('Observações', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('total_purchases_display',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_purchases_display(self, obj):
        """Display total purchases amount"""
        total = obj.total_purchases()
        return format_html('<b>R$ {:.2f}</b>', total)
    total_purchases_display.short_description = 'Total de Compras'


class OrderAdmin(admin.ModelAdmin):
    """Admin for Orders"""
    list_display = ['order_code', 'customer', 'status_badge', 'payment_method', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at', 'confirmed_at']
    search_fields = ['order_code', 'customer__full_name', 'customer__phone']
    readonly_fields = ['order_code', 'subtotal', 'total_amount', 'created_at', 'updated_at', 
                       'payment_proof_uploaded_at', 'confirmed_at', 'confirmed_by', 'payment_proof_preview']
    list_per_page = 25
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informações do Pedido', {
            'fields': ('order_code', 'customer', 'status')
        }),
        ('Pagamento', {
            'fields': ('payment_method', 'payment_proof', 'payment_proof_preview', 'payment_proof_uploaded_at')
        }),
        ('Confirmação', {
            'fields': ('confirmed_by', 'confirmed_at'),
            'classes': ('collapse',)
        }),
        ('Valores', {
            'fields': ('subtotal', 'discount', 'total_amount')
        }),
        ('Observações', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display order status with colored badge"""
        colors = {
            'PENDING': '#6c757d',
            'PAYMENT_UPLOADED': '#17a2b8',
            'CONFIRMED': '#28a745',
            'PROCESSING': '#ffc107',
            'READY': '#007bff',
            'COMPLETED': '#28a745',
            'CANCELLED': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_proof_preview(self, obj):
        """Display payment proof preview"""
        if obj.payment_proof:
            if obj.payment_proof.name.endswith(('.jpg', '.jpeg', '.png')):
                return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.payment_proof.url)
            else:
                return format_html('<a href="{}" target="_blank">Ver Comprovante</a>', obj.payment_proof.url)
        return "Sem comprovante"
    payment_proof_preview.short_description = 'Comprovante'
    
    actions = ['confirm_orders', 'mark_as_processing', 'mark_as_ready']
    
    def confirm_orders(self, request, queryset):
        """Action to confirm selected orders"""
        count = 0
        for order in queryset.filter(status='PAYMENT_UPLOADED'):
            order.confirm_payment(request.user)
            count += 1
        self.message_user(request, f'{count} pedidos confirmados.')
    confirm_orders.short_description = 'Confirmar pedidos selecionados'
    
    def mark_as_processing(self, request, queryset):
        """Action to mark orders as processing"""
        count = queryset.update(status='PROCESSING')
        self.message_user(request, f'{count} pedidos marcados como "Em Processamento".')
    mark_as_processing.short_description = 'Marcar como "Em Processamento"'
    
    def mark_as_ready(self, request, queryset):
        """Action to mark orders as ready"""
        count = queryset.update(status='READY')
        self.message_user(request, f'{count} pedidos marcados como "Pronto para Retirada".')
    mark_as_ready.short_description = 'Marcar como "Pronto para Retirada"'


class SaleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """Admin for Sales"""
    resource_class = SaleResource
    list_display = ['sale_number', 'seller', 'customer', 'status_badge', 'payment_method', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'seller', 'created_at']
    search_fields = ['sale_number', 'seller__username', 'seller__first_name', 'seller__last_name', 
                     'customer__full_name']
    readonly_fields = ['sale_number', 'subtotal', 'total_amount', 'change_amount', 'created_at', 'updated_at']
    list_per_page = 25
    inlines = [SaleItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informações da Venda', {
            'fields': ('sale_number', 'seller', 'customer', 'status')
        }),
        ('Pagamento', {
            'fields': ('payment_method', 'amount_paid', 'change_amount')
        }),
        ('Valores', {
            'fields': ('subtotal', 'discount', 'total_amount')
        }),
        ('Observações', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display sale status with colored badge"""
        colors = {
            'COMPLETED': '#28a745',
            'CANCELLED': '#dc3545',
            'REFUNDED': '#ffc107'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


class WeeklySalesReportAdmin(admin.ModelAdmin):
    """Admin for Weekly Sales Reports"""
    list_display = ['week_display', 'total_sales', 'total_orders', 'total_revenue_display', 
                    'total_profit_display', 'is_finalized', 'created_at']
    list_filter = ['year', 'is_finalized', 'created_at']
    search_fields = ['week_number', 'year']
    readonly_fields = ['year', 'week_number', 'start_date', 'end_date', 'total_sales', 
                       'total_revenue', 'total_cost', 'total_profit', 'total_orders', 
                       'created_at', 'updated_at']
    list_per_page = 25
    inlines = [SellerPerformanceInline]
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Período', {
            'fields': ('year', 'week_number', 'start_date', 'end_date')
        }),
        ('Estatísticas', {
            'fields': ('total_sales', 'total_orders', 'total_revenue', 'total_cost', 'total_profit')
        }),
        ('Status', {
            'fields': ('is_finalized',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def week_display(self, obj):
        """Display week in friendly format"""
        return format_html('<b>Semana {}/{}</b>', obj.week_number, obj.year)
    week_display.short_description = 'Semana'
    
    def total_revenue_display(self, obj):
        """Display total revenue formatted"""
        return format_html('<b style="color: green;">R$ {:.2f}</b>', obj.total_revenue)
    total_revenue_display.short_description = 'Receita Total'
    
    def total_profit_display(self, obj):
        """Display total profit formatted"""
        color = 'green' if obj.total_profit >= 0 else 'red'
        return format_html('<b style="color: {};">R$ {:.2f}</b>', color, obj.total_profit)
    total_profit_display.short_description = 'Lucro Total'
    
    actions = ['generate_reports', 'finalize_reports']
    
    def generate_reports(self, request, queryset):
        """Action to regenerate selected reports"""
        for report in queryset:
            WeeklySalesReport.generate_report(report.start_date)
        self.message_user(request, f'{queryset.count()} relatórios atualizados.')
    generate_reports.short_description = 'Regenerar relatórios selecionados'
    
    def finalize_reports(self, request, queryset):
        """Action to finalize selected reports"""
        count = queryset.update(is_finalized=True)
        self.message_user(request, f'{count} relatórios finalizados.')
    finalize_reports.short_description = 'Finalizar relatórios'


class SellerPerformanceAdmin(admin.ModelAdmin):
    """Admin for Seller Performance"""
    list_display = ['seller', 'weekly_report', 'total_sales', 'total_revenue_display', 
                    'total_items_sold', 'average_sale_value']
    list_filter = ['weekly_report__year', 'weekly_report__week_number', 'seller']
    search_fields = ['seller__username', 'seller__first_name', 'seller__last_name']
    readonly_fields = ['weekly_report', 'seller', 'total_sales', 'total_revenue', 
                       'total_items_sold', 'average_sale_value']
    list_per_page = 25
    
    def total_revenue_display(self, obj):
        """Display total revenue formatted"""
        return format_html('<b style="color: green;">R$ {:.2f}</b>', obj.total_revenue)
    total_revenue_display.short_description = 'Receita Total'


class AuditLogAdmin(admin.ModelAdmin):
    """Admin for Audit Logs"""
    list_display = ['created_at', 'user', 'action', 'model_name', 'description_short', 'ip_address']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'description', 'model_name', 'ip_address']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'description', 
                       'ip_address', 'user_agent', 'changes', 'created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informações da Ação', {
            'fields': ('user', 'action', 'model_name', 'object_id')
        }),
        ('Detalhes', {
            'fields': ('description', 'changes')
        }),
        ('Informações Técnicas', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def description_short(self, obj):
        """Display shortened description"""
        if len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description
    description_short.short_description = 'Descrição'
    
    def has_add_permission(self, request):
        """Disable manual creation of audit logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deletion of audit logs"""
        return False


class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notifications"""
    list_display = ['id', 'user', 'notification_type_badge', 'title', 'is_read', 'created_at_display']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Link e Referência', {
            'fields': ('link', 'related_object_type', 'related_object_id')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at', 'read_at')
        }),
    )
    
    def notification_type_badge(self, obj):
        """Display notification type with badge"""
        color = obj.get_color()
        icon = obj.get_icon()
        return format_html(
            '<span class="badge bg-{}" style="font-size: 0.8em;">'
            '<i class="bi {}"></i> {}</span>',
            color, icon, obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Tipo'
    
    def created_at_display(self, obj):
        """Display created date formatted"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_display.short_description = 'Criado em'
    created_at_display.admin_order_field = 'created_at'
    
    def has_add_permission(self, request):
        """Disable manual creation (notifications are auto-generated)"""
        return False


# ============================================================================
# ADMIN SITE REGISTRATION
# ============================================================================

# Import custom admin site
from .admin_site import pdv_admin_site

# Register all models with custom admin site
pdv_admin_site.register(Category, CategoryAdmin)
pdv_admin_site.register(UnitOfMeasure, UnitOfMeasureAdmin)
pdv_admin_site.register(Product, ProductAdmin)
pdv_admin_site.register(UserProfile, UserProfileAdmin)
pdv_admin_site.register(Customer, CustomerAdmin)
pdv_admin_site.register(Order, OrderAdmin)
pdv_admin_site.register(Sale, SaleAdmin)
pdv_admin_site.register(WeeklySalesReport, WeeklySalesReportAdmin)
pdv_admin_site.register(SellerPerformance, SellerPerformanceAdmin)
pdv_admin_site.register(AuditLog, AuditLogAdmin)
pdv_admin_site.register(Notification, NotificationAdmin)
