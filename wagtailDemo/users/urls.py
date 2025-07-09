from django.urls import path
from . import views
from .docs import api_documentation
from .admin_views import user_dashboard

app_name = 'users'

urlpatterns = [
    path('api/auth/send-otp/', views.send_otp, name='send_otp'),
    path('api/auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/auth/profile/', views.user_profile, name='user_profile'),
    path('api/auth/docs/', api_documentation, name='api_docs'),
    
    # Admin dashboard (only accessible to staff)
    path('admin/users/dashboard/', user_dashboard, name='user_dashboard'),
]
