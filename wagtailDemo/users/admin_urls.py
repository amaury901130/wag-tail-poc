from django.urls import path, include
from .admin_views import user_dashboard

app_name = 'users_admin'

urlpatterns = [
    path('dashboard/', user_dashboard, name='dashboard'),
]
