from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from ..models import OTPCode

User = get_user_model()


class UserAdminViewsTest(TestCase):
    """Test cases for user admin views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create a staff user for testing admin views
        self.staff_user = User.objects.create_user(
            username='admin',
            phone_number='+1111111111',
            role=User.Role.ADMIN  # Use role instead of is_staff/is_superuser
        )
        
        # Create some test users
        self.regular_user = User.objects.create_user(
            username='user1',
            phone_number='+1234567890',
            is_phone_verified=True
        )
        
        self.unverified_user = User.objects.create_user(
            username='user2', 
            phone_number='+1987654321',
            is_phone_verified=False
        )
        
        # Create some test OTP codes
        OTPCode.objects.create(
            phone_number='+1234567890',
            is_used=True
        )
        
        OTPCode.objects.create(
            phone_number='+1987654321',
            is_used=False,
            expires_at=timezone.now() - timedelta(minutes=1)  # Expired
        )
    
    def test_user_dashboard_requires_staff(self):
        """Test that dashboard requires staff access"""
        url = '/admin/user-management/dashboard/'
        
        # Test unauthenticated access
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test non-staff user access
        self.client.force_login(self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test staff user access
        self.client.force_login(self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_user_dashboard_content(self):
        """Test dashboard displays correct statistics"""
        self.client.force_login(self.staff_user)
        url = '/admin/user-management/dashboard/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check context data
        context = response.context
        self.assertIn('stats', context)
        self.assertIn('otp_stats', context)
        self.assertIn('recent_users', context)
        self.assertIn('recent_otps', context)
        
        # Check statistics
        stats = context['stats']
        self.assertEqual(stats['total_users'], 3)  # admin + 2 test users
        self.assertEqual(stats['verified_users'], 1)  # Only regular_user is verified
        self.assertEqual(stats['unverified_users'], 2)  # admin and unverified_user
        
        # Check OTP statistics
        otp_stats = context['otp_stats']
        self.assertEqual(otp_stats['total_otps'], 2)
        self.assertEqual(otp_stats['used_otps'], 1)
    
    def test_user_dashboard_template(self):
        """Test dashboard uses correct template"""
        self.client.force_login(self.staff_user)
        url = '/admin/user-management/dashboard/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailadmin/users/dashboard.html')
        
        # Check that important elements are in the response
        content = response.content.decode()
        self.assertIn('User Management Dashboard', content)
        self.assertIn('Total Users', content)
        self.assertIn('Verified Users', content)
        self.assertIn('Recent Users', content)
        self.assertIn('OTP Statistics', content)
