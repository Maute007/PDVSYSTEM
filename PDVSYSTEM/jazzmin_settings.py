# Jazzmin Configuration for PDV System Admin

JAZZMIN_SETTINGS = {
    # Site branding
    "site_title": "PDV System Admin",
    "site_header": "PDV System",
    "site_brand": "Gestão de Vendas",
    "site_logo": None,
    "login_logo": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Bem-vindo ao Painel Administrativo",
    "copyright": "PDV System © 2025",
    
    # Search model
    "search_model": ["auth.User", "loja.Product", "loja.Customer"],
    
    # User menu
    "user_avatar": None,
    
    # Top menu
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:dashboard", "permissions": ["auth.view_user"]},
        {"name": "Relatórios", "url": "admin:sales_reports", "permissions": ["loja.view_sale"]},
        {"name": "Site", "url": "/", "new_window": True},
        {"model": "auth.User"},
        {"app": "loja"},
    ],
    
    # Side menu customization
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Custom icons for models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "loja.Category": "fas fa-tags",
        "loja.Product": "fas fa-box",
        "loja.UnitOfMeasure": "fas fa-balance-scale",
        "loja.Sale": "fas fa-cash-register",
        "loja.SaleItem": "fas fa-shopping-cart",
        "loja.Order": "fas fa-receipt",
        "loja.OrderItem": "fas fa-list",
        "loja.Customer": "fas fa-user-tie",
        "loja.UserProfile": "fas fa-id-card",
        "loja.WeeklySalesReport": "fas fa-chart-line",
        "loja.SellerPerformance": "fas fa-trophy",
        "loja.AuditLog": "fas fa-history",
        "loja.Notification": "fas fa-bell",
    },
    
    # Custom CSS/JS
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": None,
    
    # Show/hide related modal
    "related_modal_active": True,
    
    # UI Tweaks
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs"
    },
    
    # Default icon parents
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Language chooser
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",  # Tema claro e moderno
    "dark_mode_theme": None, # Desativar modo escuro
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    # Custom colors inspired by 6valley
    "actions_sticky_top": True,
}
