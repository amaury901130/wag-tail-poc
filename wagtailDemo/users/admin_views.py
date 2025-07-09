from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from wagtail.admin.ui.components import Component

from .models import User, OTPCode


@staff_member_required
def user_dashboard(request):
    """Custom dashboard view for user statistics"""
    
    # Calculate date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User statistics
    total_users = User.objects.count()
    verified_users = User.objects.filter(is_phone_verified=True).count()
    unverified_users = total_users - verified_users
    
    # Recent user registrations
    users_this_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    users_this_month = User.objects.filter(date_joined__date__gte=month_ago).count()
    
    # OTP statistics
    total_otps = OTPCode.objects.count()
    used_otps = OTPCode.objects.filter(is_used=True).count()
    expired_otps = OTPCode.objects.filter(
        expires_at__lt=timezone.now(),
        is_used=False
    ).count()
    
    # Recent OTP activity
    otps_today = OTPCode.objects.filter(created_at__date=today).count()
    otps_this_week = OTPCode.objects.filter(created_at__date__gte=week_ago).count()
    
    # Recent users
    recent_users = User.objects.select_related().order_by('-date_joined')[:10]
    
    # Recent OTP codes
    recent_otps = OTPCode.objects.order_by('-created_at')[:10]
    
    context = {
        'title': 'User Management Dashboard',
        'stats': {
            'total_users': total_users,
            'verified_users': verified_users,
            'unverified_users': unverified_users,
            'users_this_week': users_this_week,
            'users_this_month': users_this_month,
            'verification_rate': round((verified_users / total_users * 100) if total_users > 0 else 0, 1),
        },
        'otp_stats': {
            'total_otps': total_otps,
            'used_otps': used_otps,
            'expired_otps': expired_otps,
            'otps_today': otps_today,
            'otps_this_week': otps_this_week,
            'success_rate': round((used_otps / total_otps * 100) if total_otps > 0 else 0, 1),
        },
        'recent_users': recent_users,
        'recent_otps': recent_otps,
    }
    
    return render(request, 'wagtailadmin/users/dashboard.html', context)
