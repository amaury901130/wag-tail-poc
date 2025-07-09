from django.urls import path
from . import views
from .docs import api_documentation

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('api/auth/send-otp/', views.SendOTPView.as_view(), name='send_otp'),
    path('api/auth/verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    
    # User profile endpoints
    path('api/auth/profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Documentation
    path('api/auth/docs/', api_documentation, name='api_docs'),
]
