"""
Views for PDV System
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.db import transaction
from datetime import timedelta, datetime
from functools import wraps
from decimal import Decimal
import json
from .models import (
    Category, Product, Customer, Order, OrderItem, Sale, SaleItem,
    WeeklySalesReport, UserProfile, AuditLog, Notification
)


# ========== DECORADORES DE PERMISSÃO ==========

def role_required(*roles):
    """
    Decorator to restrict access based on user role
    Usage: @role_required('SELLER', 'MANAGER', 'ADMIN')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                user_profile = request.user.profile
                if user_profile.role in roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'Você não tem permissão para acessar esta página.')
                    return redirect('home')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Perfil de usuário não encontrado.')
                return redirect('login')
        
        return wrapper

        #print(f'User {request.user.username} with role {user_profile.role} attempted to access {view_func.__name__} requiring roles {roles}')
    return decorator


def seller_required(view_func):
    """Shortcut for seller, manager, and admin access"""
    return role_required('SELLER', 'MANAGER', 'ADMIN')(view_func)


def manager_required(view_func):
    """Shortcut for manager and admin access only"""
    return role_required('MANAGER', 'ADMIN')(view_func)


def admin_required(view_func):
    """Shortcut for admin access only"""
    return role_required('ADMIN')(view_func)


# ========== VIEWS ==========

@login_required
@seller_required
def home(request):
    """
    Homepage with dashboard statistics
    Data shown depends on user role:
    - SELLER: Only today's data
    - MANAGER/ADMIN: All data
    """
    user_profile = request.user.profile
    today = timezone.now().date()
    
    # Base query filters
    if user_profile.role == 'SELLER':
        # Vendedor vê apenas dados de hoje e suas próprias vendas
        sales_filter = Q(created_at__date=today) & Q(seller=request.user)
        orders_filter = Q(created_at__date=today)
    else:
        # Gerente e Admin veem tudo de hoje
        sales_filter = Q(created_at__date=today)
        orders_filter = Q(created_at__date=today)
    
    # Estatísticas de vendas
    today_sales = Sale.objects.filter(sales_filter, status='COMPLETED')
    total_sales_today = today_sales.count()
    revenue_today = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Pedidos pendentes
    pending_orders = Order.objects.filter(
        orders_filter,
        status__in=['PENDING', 'PAYMENT_UPLOADED']
    ).count()
    
    # Produtos com estoque baixo
    low_stock_products = Product.objects.filter(
        stock_status='LOW_STOCK',
        is_active=True
    ).count()
    
    # Vendas recentes (últimas 10)
    recent_sales = Sale.objects.filter(sales_filter).select_related(
        'seller', 'customer'
    ).prefetch_related('items').order_by('-created_at')[:10]
    
    # Pedidos recentes pendentes
    recent_orders = Order.objects.filter(
        orders_filter,
        status__in=['PENDING', 'PAYMENT_UPLOADED']
    ).select_related('customer').order_by('-created_at')[:5]
    
    context = {
        'user_role': user_profile.role,
        'total_sales_today': total_sales_today,
        'revenue_today': revenue_today,
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'recent_orders': recent_orders,
        'today': today,
    }
    return render(request, 'home.html', context)


@login_required
@seller_required
def produtos(request):
    """
    Products listing page
    All roles can view products, filtered by active status and search
    """
    # Filtros de pesquisa
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    
    # Query base
    products = Product.objects.filter(is_active=True).select_related(
        'category', 'unit_of_measure'
    )
    
    # Aplicar filtros
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(barcode__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if status_filter:
        products = products.filter(stock_status=status_filter)
    
    # Ordenar por nome
    products = products.order_by('name')
    
    # Categorias para o filtro
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }
    return render(request, 'produtos.html', context)


@login_required
@seller_required
def nova_venda(request):
    """
    New sale page (POS System)
    All seller roles can create sales
    """
    # Produtos ativos com estoque
    products = Product.objects.filter(
        is_active=True,
        stock_status__in=['IN_STOCK', 'LOW_STOCK']
    ).select_related('category', 'unit_of_measure').order_by('name')
    
    # Clientes ativos
    customers = Customer.objects.filter(is_active=True).order_by('full_name')
    
    # Métodos de pagamento
    payment_methods = Sale.PAYMENT_METHOD_CHOICES
    
    context = {
        'products': products,
        'customers': customers,
        'payment_methods': payment_methods,
        'seller': request.user,
    }
    return render(request, 'nova_venda.html', context)


@login_required
@seller_required
def pedidos(request):
    """
    Orders listing page
    SELLER: Only today's orders
    MANAGER/ADMIN: All orders with filters
    """
    user_profile = request.user.profile
    today = timezone.now().date()
    
    # Filtros de pesquisa
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    # Query base
    orders = Order.objects.select_related('customer', 'confirmed_by').prefetch_related('items')
    
    # Vendedor vê apenas pedidos de hoje
    if user_profile.role == 'SELLER':
        orders = orders.filter(created_at__date=today)
    else:
        # Gerente e Admin podem filtrar por data
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date=filter_date)
            except ValueError:
                pass
    
    # Aplicar filtros
    if search_query:
        orders = orders.filter(
            Q(order_code__icontains=search_query) |
            Q(customer__full_name__icontains=search_query) |
            Q(customer__phone__icontains=search_query)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Ordenar por mais recente
    orders = orders.order_by('-created_at')
    
    # Estatísticas de pedidos
    stats = {
        'pending': orders.filter(status='PENDING').count(),
        'payment_uploaded': orders.filter(status='PAYMENT_UPLOADED').count(),
        'confirmed': orders.filter(status='CONFIRMED').count(),
        'completed': orders.filter(status='COMPLETED').count(),
    }
    
    context = {
        'orders': orders,
        'stats': stats,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'user_role': user_profile.role,
        'today': today,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'pedidos.html', context)


@login_required
@manager_required
def relatorios(request):
    """
    Reports and analytics page
    ONLY MANAGER and ADMIN can access
    """
    # Filtros de período
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Período padrão: últimos 30 dias
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    
    # Estatísticas do período
    period_sales = Sale.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='COMPLETED'
    )
    
    total_revenue = period_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_sales = period_sales.count()
    
    # Calcular lucro (receita - custo)
    total_cost = 0
    for sale in period_sales.prefetch_related('items__product'):
        for item in sale.items.all():
            total_cost += item.product.cost_price * item.quantity
    
    total_profit = float(total_revenue) - float(total_cost)
    
    # Ticket médio
    average_ticket = total_revenue / total_sales if total_sales > 0 else 0
    
    # Relatórios semanais no período
    weekly_reports = WeeklySalesReport.objects.filter(
        start_date__gte=start_date,
        end_date__lte=end_date
    ).order_by('-year', '-week_number')
    
    # Top 5 vendedores do período
    from django.db.models import Count, Sum
    top_sellers = Sale.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='COMPLETED'
    ).values(
        'seller__username',
        'seller__first_name',
        'seller__last_name'
    ).annotate(
        total_sales=Count('id'),
        total_revenue=Sum('total_amount')
    ).order_by('-total_revenue')[:5]
    
    # Top 10 produtos mais vendidos
    top_products = SaleItem.objects.filter(
        sale__created_at__date__gte=start_date,
        sale__created_at__date__lte=end_date,
        sale__status='COMPLETED'
    ).values(
        'product__name',
        'product__unit_of_measure__abbreviation'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_revenue')[:10]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'total_profit': total_profit,
        'average_ticket': average_ticket,
        'weekly_reports': weekly_reports,
        'top_sellers': top_sellers,
        'top_products': top_products,
    }
    return render(request, 'relatorios.html', context)


# ========== API VIEWS FOR AJAX ==========

@login_required
@seller_required
@require_http_methods(["GET"])
def api_get_product(request, product_id):
    """
    API endpoint to get product details with real-time stock
    Returns JSON with product info and available quantity
    """
    try:
        product = Product.objects.select_related('category', 'unit_of_measure').get(
            id=product_id,
            is_active=True
        )
        
        # Calculate available stock
        available = product.stock_quantity
        can_sell = available > 0 and product.stock_status != 'OUT_OF_STOCK'
        
        data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'category': product.category.name,
            'unit_price': float(product.unit_price),
            'cost_price': float(product.cost_price),
            'stock_quantity': float(product.stock_quantity),
            'minimum_stock': float(product.minimum_stock),
            'stock_status': product.stock_status,
            'unit_of_measure': product.unit_of_measure.abbreviation,
            'allows_fraction': product.unit_of_measure.allows_fraction,
            'allows_bulk_sale': product.allows_bulk_sale,
            'can_sell': can_sell,
            'image_url': product.image.url if product.image else None,
        }
        
        return JsonResponse({'success': True, 'product': data})
    
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'}, status=404)


@login_required
@seller_required
@require_http_methods(["POST"])
def api_validate_quantity(request):
    """
    API endpoint to validate if quantity is available
    Returns remaining stock after hypothetical sale
    """
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = Decimal(str(data.get('quantity', 0)))
        
        product = Product.objects.get(id=product_id, is_active=True)
        
        # Check if quantity is valid
        if quantity <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Quantidade deve ser maior que zero'
            })
        
        # Check if product allows fraction
        if not product.allows_bulk_sale and quantity % 1 != 0:
            return JsonResponse({
                'success': False,
                'error': 'Este produto não permite venda fracionada'
            })
        
        # Check stock availability
        remaining = product.stock_quantity - quantity
        
        if remaining < 0:
            return JsonResponse({
                'success': False,
                'error': f'Estoque insuficiente. Disponível: {product.stock_quantity} {product.unit_of_measure.abbreviation}'
            })
        
        # Calculate totals
        total_price = quantity * product.unit_price
        
        return JsonResponse({
            'success': True,
            'remaining_stock': float(remaining),
            'total_price': float(total_price),
            'unit_price': float(product.unit_price),
            'will_be_low_stock': remaining <= product.minimum_stock and remaining > 0,
            'will_be_out_of_stock': remaining == 0
        })
    
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'}, status=404)
    except (ValueError, KeyError) as e:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)


@login_required
@seller_required
@require_http_methods(["POST"])
@transaction.atomic
def api_process_sale(request):
    """
    Process a new sale with stock validation and audit trail
    Limit: Non-admin users can only make 5 sales per day
    """
    try:
        # Log received data
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Received sale request from {request.user.username}")
        logger.info(f"Request body: {request.body.decode('utf-8')}")
        
        # Check daily limit for non-admin users
        user_profile = request.user.profile
        if user_profile.role not in ['ADMIN']:
            today = timezone.now().date()
            today_sales_count = Sale.objects.filter(
                seller=request.user,
                created_at__date=today,
                status='COMPLETED'
            ).count()
            
            if today_sales_count >= 5:
                return JsonResponse({
                    'success': False,
                    'error': 'Limite diário atingido! Você só pode fazer 5 vendas por dia. Contacte o administrador.'
                }, status=403)
        
        data = json.loads(request.body)
        logger.info(f"Parsed data: {data}")
        
        # Validate required fields
        items = data.get('items', [])
        customer_id = data.get('customer_id')
        payment_method = data.get('payment_method')
        
        if not items:
            logger.error("No items in sale")
            return JsonResponse({'success': False, 'error': 'Nenhum item na venda'}, status=400)
        
        if not payment_method:
            logger.error("No payment method")
            return JsonResponse({'success': False, 'error': 'Método de pagamento não informado'}, status=400)
        
        # Parse amounts with defaults
        try:
            amount_paid = Decimal(str(data.get('amount_paid', 0)))
            discount = Decimal(str(data.get('discount', 0)))
        except Exception as e:
            logger.error(f"Error parsing amounts: {e}")
            amount_paid = Decimal('0')
            discount = Decimal('0')
        
        # Get or create customer
        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                logger.warning(f"Customer {customer_id} not found")
                pass
        
        # Create sale
        sale = Sale.objects.create(
            seller=request.user,
            customer=customer,
            payment_method=payment_method,
            discount=discount,
            amount_paid=amount_paid,
            status='COMPLETED'
        )
        
        logger.info(f"Sale created with ID: {sale.id}, sale_number: {sale.sale_number}")
        
        subtotal = Decimal('0')
        
        # Process each item
        for item_data in items:
            try:
                logger.info(f"Processing item: {item_data}")
                product_id = int(item_data.get('product_id'))
                quantity = Decimal(str(item_data.get('quantity')))
                
                if quantity <= 0:
                    raise ValueError(f'Quantidade inválida: {quantity}')
                
                logger.info(f"Getting product {product_id}")
                product = Product.objects.select_for_update().get(id=product_id)
                logger.info(f"Product found: {product.name}, stock: {product.stock_quantity}")
                
                # Validate stock
                if product.stock_quantity < quantity:
                    raise ValueError(f'Estoque insuficiente para {product.name}. Disponível: {product.stock_quantity}')
                
                # Create sale item
                unit_price = product.unit_price
                total_price = quantity * unit_price
                
                logger.info(f"Creating sale item for sale.id={sale.id}")
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                logger.info(f"Sale item created successfully")
                
                # Update stock
                product.stock_quantity -= quantity
                product.update_stock_status()
                product.save()
                logger.info(f"Stock updated for {product.name}")
                
                subtotal += total_price
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing item: {e}")
                raise ValueError(f'Erro ao processar item: {str(e)}')
        
        # Update sale totals
        sale.subtotal = subtotal
        sale.total_amount = subtotal - discount
        sale.change_amount = amount_paid - sale.total_amount
        sale.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='SALE_COMPLETE',
            model_name='Sale',
            object_id=sale.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            changes={
                'sale_number': sale.sale_number,
                'total_amount': float(sale.total_amount),
                'items_count': len(items)
            }
        )
        
        return JsonResponse({
            'success': True,
            'sale_id': sale.id,
            'sale_number': sale.sale_number,
            'total_amount': float(sale.total_amount),
            'change_amount': float(sale.change_amount)
        })
    
    except Customer.DoesNotExist:
        logger.error("Customer not found")
        return JsonResponse({'success': False, 'error': 'Cliente não encontrado'}, status=404)
    except Product.DoesNotExist as e:
        logger.error(f"Product not found: {e}")
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'}, status=404)
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'success': False, 'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error in api_process_sale: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"Error in api_process_sale: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': f'Erro ao processar venda: {str(e)}'}, status=500)


@login_required
@seller_required
@require_http_methods(["POST"])
@transaction.atomic
def api_confirm_order(request, order_id):
    """
    Confirm an order and update stock
    Only managers and admins can confirm orders
    """
    if request.user.profile.role not in ['MANAGER', 'ADMIN']:
        return JsonResponse({'success': False, 'error': 'Sem permissão'}, status=403)
    
    try:
        order = Order.objects.select_for_update().get(id=order_id)
        
        # Validate order status
        if order.status not in ['PENDING', 'PAYMENT_UPLOADED']:
            return JsonResponse({
                'success': False,
                'error': 'Pedido não pode ser confirmado neste status'
            }, status=400)
        
        # Check stock for all items
        for item in order.items.all():
            if item.product.stock_quantity < item.quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Estoque insuficiente para {item.product.name}'
                }, status=400)
        
        # Update stock
        for item in order.items.all():
            product = item.product
            product.stock_quantity -= item.quantity
            product.update_stock_status()
            product.save()
        
        # Confirm order
        order.confirm_payment(request.user)
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='ORDER_CONFIRM',
            model_name='Order',
            object_id=order.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            changes={
                'order_code': order.order_code,
                'customer': order.customer.full_name,
                'total_amount': float(order.total_amount)
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Pedido confirmado com sucesso',
            'order_code': order.order_code
        })
    
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@seller_required
@require_http_methods(["POST"])
def api_cancel_order(request, order_id):
    """
    Cancel an order
    """
    if request.user.profile.role not in ['MANAGER', 'ADMIN']:
        return JsonResponse({'success': False, 'error': 'Sem permissão'}, status=403)
    
    try:
        order = Order.objects.get(id=order_id)
        
        if order.status in ['COMPLETED', 'CANCELLED']:
            return JsonResponse({
                'success': False,
                'error': 'Pedido não pode ser cancelado neste status'
            }, status=400)
        
        order.status = 'CANCELLED'
        order.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='ORDER_CANCEL',
            model_name='Order',
            object_id=order.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            changes={'order_code': order.order_code}
        )
        
        return JsonResponse({'success': True, 'message': 'Pedido cancelado'})
    
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido não encontrado'}, status=404)


@login_required
@seller_required
def api_search_products(request):
    """
    Search products by name, code, or barcode
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'success': True, 'products': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(code__icontains=query) |
        Q(barcode__icontains=query),
        is_active=True
    ).select_related('category', 'unit_of_measure')[:20]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'code': product.code,
            'category': product.category.name,
            'unit_price': float(product.unit_price),
            'stock_quantity': float(product.stock_quantity),
            'stock_status': product.stock_status,
            'unit': product.unit_of_measure.abbreviation,
            'can_sell': product.stock_quantity > 0 and product.stock_status != 'OUT_OF_STOCK'
        })
    
    return JsonResponse({'success': True, 'products': results})


# ========== NOTIFICATION VIEWS ==========

@login_required
@seller_required
def api_get_notifications(request):
    """
    Get user's unread notifications
    """
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:20]
    
    results = []
    for notif in notifications:
        results.append({
            'id': notif.id,
            'type': notif.notification_type,
            'title': notif.title,
            'message': notif.message,
            'link': notif.link,
            'icon': notif.get_icon(),
            'color': notif.get_color(),
            'created_at': notif.created_at.strftime('%d/%m/%Y %H:%M'),
            'time_ago': get_time_ago(notif.created_at)
        })
    
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    return JsonResponse({
        'success': True,
        'notifications': results,
        'unread_count': unread_count
    })


@login_required
@seller_required
@require_http_methods(["POST"])
def api_mark_notification_read(request, notification_id):
    """
    Mark notification as read
    """
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificação não encontrada'}, status=404)


@login_required
@seller_required
@require_http_methods(["POST"])
def api_mark_all_notifications_read(request):
    """
    Mark all notifications as read
    """
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Todas as notificações foram marcadas como lidas'
    })


def get_time_ago(dt):
    """
    Convert datetime to relative time string
    """
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return 'Agora mesmo'
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f'Há {minutes} minuto{"s" if minutes > 1 else ""}'
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'Há {hours} hora{"s" if hours > 1 else ""}'
    elif diff < timedelta(days=7):
        days = diff.days
        return f'Há {days} dia{"s" if days > 1 else ""}'
    else:
        return dt.strftime('%d/%m/%Y')

