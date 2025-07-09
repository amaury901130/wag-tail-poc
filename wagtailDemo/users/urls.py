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
    
    # Users endpoints
    path('api/auth/users/', views.UserListView.as_view(), name='user_list'),
    path('api/auth/users/<int:pk>/role/', views.UserRoleUpdateView.as_view(), name='update_user_role'),
    
    # Documentation
    path('api/auth/docs/', api_documentation, name='api_docs'),
]
