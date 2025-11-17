from django.urls import path
from loja import views

urlpatterns = [
    path('', views.home, name='home'),
    path('produtos/', views.produtos, name='produtos'),
    path('nova-venda/', views.nova_venda, name='nova_venda'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('relatorios/', views.relatorios, name='relatorios'),
    
    # API endpoints
    path('api/product/<int:product_id>/', views.api_get_product, name='api_get_product'),
    path('api/validate-quantity/', views.api_validate_quantity, name='api_validate_quantity'),
    path('api/process-sale/', views.api_process_sale, name='api_process_sale'),
    path('api/search-products/', views.api_search_products, name='api_search_products'),
    path('api/order/<int:order_id>/confirm/', views.api_confirm_order, name='api_confirm_order'),
    path('api/order/<int:order_id>/cancel/', views.api_cancel_order, name='api_cancel_order'),
    
    # Notification endpoints
    path('api/notifications/', views.api_get_notifications, name='api_get_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/mark-all-read/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),
]
