from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtail import hooks

from .models import User, OTPCode


class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    list_display = ('username', 'phone_number', 'is_phone_verified', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_phone_verified', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Phone Authentication', {
            'fields': ('phone_number', 'is_phone_verified')
        }),
    )


class OTPCodeAdmin(admin.ModelAdmin):
    """Admin for OTP codes"""
    list_display = ('phone_number', 'code', 'is_used', 'created_at', 'expires_at', 'is_valid_display')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('phone_number', 'code')
    readonly_fields = ('code', 'created_at', 'expires_at')
    ordering = ('-created_at',)
    
    def is_valid_display(self, obj):
        """Display if OTP is currently valid"""
        return obj.is_valid()
    is_valid_display.short_description = 'Valid'
    is_valid_display.boolean = True


# Register with Django admin
admin.site.register(User, UserAdmin)
admin.site.register(OTPCode, OTPCodeAdmin)

# Register OTPCode as a Wagtail snippet for easy access in Wagtail admin
@register_snippet
class OTPCodeSnippet(OTPCode):
    """OTPCode as a Wagtail snippet"""
    
    panels = [
        FieldPanel('phone_number'),
        FieldPanel('code'),
        FieldPanel('is_used'),
        FieldPanel('expires_at'),
    ]
    
    class Meta:
        proxy = True
        verbose_name = "OTP Code"
        verbose_name_plural = "OTP Codes"


# Register User as a Wagtail snippet for easy management
@register_snippet
class UserSnippet(User):
    """User as a Wagtail snippet"""
    
    panels = [
        MultiFieldPanel([
            FieldPanel("username"),
            FieldPanel("first_name"),
            FieldPanel("last_name"),
            FieldPanel("email"),
        ], heading="User Information"),
        
        MultiFieldPanel([
            FieldPanel("phone_number"),
            FieldPanel("is_phone_verified"),
        ], heading="Phone Authentication"),
        
        MultiFieldPanel([
            FieldPanel("is_active"),
            FieldPanel("is_staff"),
            FieldPanel("is_superuser"),
        ], heading="Permissions"),
    ]
    
    class Meta:
        proxy = True
        verbose_name = "User"
        verbose_name_plural = "Users"


# Add dashboard to admin menu
@hooks.register('register_admin_menu_item')
def register_user_dashboard_menu_item():
    from wagtail.admin.menu import MenuItem
    return MenuItem(
        'User Dashboard', 
        '/admin/user-management/dashboard/', 
        icon_name='user',
        order=99
    )


# Register admin URLs
@hooks.register('register_admin_urls')
def register_admin_urls():
    from django.urls import path, include
    return [
        path('user-management/', include('wagtailDemo.users.admin_urls', namespace='users_admin')),
    ]
