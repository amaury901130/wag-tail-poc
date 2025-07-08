from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

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
