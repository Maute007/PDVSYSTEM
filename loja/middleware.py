"""
Custom Middleware for PDV System
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import UserProfile


class RoleBasedAccessMiddleware:
    """
    Middleware to control access based on user role
    - CUSTOMER role cannot access any page (redirect to login with message)
    - Creates UserProfile if it doesn't exist
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip for anonymous users and authentication pages
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip for admin pages, static files, media files
        if request.path.startswith('/admin/') or \
           request.path.startswith('/static/') or \
           request.path.startswith('/media/') or \
           request.path.startswith('/accounts/logout/'):
            return self.get_response(request)
        
        # Create UserProfile if it doesn't exist
        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist:
            # Create default profile for users without one
            user_profile = UserProfile.objects.create(
                user=request.user,
                role='CUSTOMER'  # Default role
            )
            messages.warning(
                request,
                'Perfil criado. Contacte o administrador para definir suas permissões.'
            )
        
        # Block CUSTOMER role from accessing any page
        if user_profile.role == 'CUSTOMER':
            # Allow logout
            if request.path == reverse('logout'):
                return self.get_response(request)
            
            # Redirect to login with message
            messages.error(
                request,
                'Clientes não têm acesso ao sistema. Contacte o administrador.'
            )
            from django.contrib.auth import logout
            logout(request)
            return redirect('login')
        
        return self.get_response(request)
