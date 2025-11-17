"""
Signals for PDV System
Automatically create UserProfile when a User is created
"""
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, Product, Sale, Order, Notification


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create UserProfile when a new User is created
    """
    if created:
        UserProfile.objects.create(
            user=instance,
            role='CUSTOMER'  # Default role, admin should change it
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile when User is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=Product)
def notify_product_changes(sender, instance, created, **kwargs):
    """
    Send notifications when product is added or stock changes
    """
    # Notify all managers and admins
    managers = User.objects.filter(
        profile__role__in=['MANAGER', 'ADMIN'],
        is_active=True
    )
    
    if created:
        # New product added
        for manager in managers:
            Notification.notify_product_added(manager, instance)
    else:
        # Check stock status
        if instance.stock_status == 'OUT_OF_STOCK':
            for manager in managers:
                # Check if notification already exists
                exists = Notification.objects.filter(
                    user=manager,
                    notification_type='OUT_OF_STOCK',
                    related_object_id=instance.id,
                    is_read=False
                ).exists()
                
                if not exists:
                    Notification.notify_out_of_stock(manager, instance)
        
        elif instance.stock_status == 'LOW_STOCK':
            for manager in managers:
                # Check if notification already exists
                exists = Notification.objects.filter(
                    user=manager,
                    notification_type='LOW_STOCK',
                    related_object_id=instance.id,
                    is_read=False
                ).exists()
                
                if not exists:
                    Notification.notify_low_stock(manager, instance)


@receiver(post_save, sender=Sale)
def notify_sales_milestone(sender, instance, created, **kwargs):
    """
    Send notification when sales milestone is reached
    """
    if created and instance.status == 'COMPLETED':
        # Count seller's total sales
        seller_sales_count = Sale.objects.filter(
            seller=instance.seller,
            status='COMPLETED'
        ).count()
        
        # Notify on milestones (50, 100, 150, etc.)
        if seller_sales_count % 50 == 0:
            Notification.notify_sales_milestone(instance.seller, seller_sales_count)


@receiver(post_save, sender=Order)
def notify_new_order(sender, instance, created, **kwargs):
    """
    Send notification when new order is received
    """
    if created:
        # Notify all sellers, managers and admins
        staff = User.objects.filter(
            profile__role__in=['SELLER', 'MANAGER', 'ADMIN'],
            is_active=True
        )
        
        for user in staff:
            Notification.notify_order_received(user, instance)
