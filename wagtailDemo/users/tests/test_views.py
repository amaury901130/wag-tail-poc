from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import OTPCode
from ..services import SMSServiceError

User = get_user_model()


class SendOTPAPITest(APITestCase):
    """Test cases for send OTP API"""
    
    def setUp(self):
        self.url = reverse('users:send_otp')
        self.valid_phone = "+1234567890"
        self.invalid_phone = "invalid"
    
    def test_send_otp_success(self):
        """Test successful OTP sending"""
        with patch('wagtailDemo.users.services.otp_service.send_otp', return_value=True):
            response = self.client.post(self.url, {
                'phone_number': self.valid_phone
            })
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['phone_number'], self.valid_phone)
            self.assertTrue(OTPCode.objects.filter(phone_number=self.valid_phone).exists())
    
    def test_send_otp_invalid_phone(self):
        """Test OTP sending with invalid phone number"""
        response = self.client.post(self.url, {
            'phone_number': self.invalid_phone
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_send_otp_service_failure(self):
        """Test OTP sending when service fails"""
        with patch('wagtailDemo.users.services.otp_service.send_otp', return_value=False):
            response = self.client.post(self.url, {
                'phone_number': self.valid_phone
            })
            
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.data)
    
    def test_send_otp_sms_service_error(self):
        """Test OTP sending when SMS service raises error"""
        with patch('wagtailDemo.users.services.otp_service.send_otp', side_effect=SMSServiceError("Service error")):
            response = self.client.post(self.url, {
                'phone_number': self.valid_phone
            })
            
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.data)
    
    def test_send_otp_invalidates_previous_codes(self):
        """Test that sending new OTP invalidates previous codes"""
        # Create initial OTP
        old_otp = OTPCode.objects.create(phone_number=self.valid_phone)
        self.assertTrue(old_otp.is_valid())
        
        with patch('wagtailDemo.users.services.otp_service.send_otp', return_value=True):
            response = self.client.post(self.url, {
                'phone_number': self.valid_phone
            })
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Refresh old OTP from database
            old_otp.refresh_from_db()
            self.assertTrue(old_otp.is_used)


class VerifyOTPAPITest(APITestCase):
    """Test cases for verify OTP API"""
    
    def setUp(self):
        self.url = reverse('users:verify_otp')
        self.valid_phone = "+1234567890"
    
    def test_verify_otp_new_user_success(self):
        """Test successful OTP verification for new user"""
        otp = OTPCode.objects.create(phone_number=self.valid_phone)
        
        response = self.client.post(self.url, {
            'phone_number': self.valid_phone,
            'otp_code': otp.code
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_new_user'])
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        
        # Check user was created
        user = User.objects.get(phone_number=self.valid_phone)
        self.assertTrue(user.is_phone_verified)
        
        # Check OTP was marked as used
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)
    
    def test_verify_otp_existing_user_success(self):
        """Test successful OTP verification for existing user"""
        # Create existing user
        user = User.objects.create_user(
            username="existing_user",
            phone_number=self.valid_phone,
            is_phone_verified=False
        )
        
        otp = OTPCode.objects.create(phone_number=self.valid_phone)
        
        response = self.client.post(self.url, {
            'phone_number': self.valid_phone,
            'otp_code': otp.code
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_new_user'])
        self.assertIn('tokens', response.data)
        
        # Check user's phone was verified
        user.refresh_from_db()
        self.assertTrue(user.is_phone_verified)
    
    def test_verify_otp_invalid_code(self):
        """Test OTP verification with invalid code"""
        OTPCode.objects.create(phone_number=self.valid_phone)
        
        response = self.client.post(self.url, {
            'phone_number': self.valid_phone,
            'otp_code': "999999"  # Wrong code
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_verify_otp_expired_code(self):
        """Test OTP verification with expired code"""
        from django.utils import timezone
        from datetime import timedelta
        
        otp = OTPCode.objects.create(
            phone_number=self.valid_phone,
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        
        response = self.client.post(self.url, {
            'phone_number': self.valid_phone,
            'otp_code': otp.code
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_verify_otp_used_code(self):
        """Test OTP verification with already used code"""
        otp = OTPCode.objects.create(phone_number=self.valid_phone)
        otp.mark_as_used()
        
        response = self.client.post(self.url, {
            'phone_number': self.valid_phone,
            'otp_code': otp.code
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_verify_otp_invalid_format(self):
        """Test OTP verification with invalid format"""
        response = self.client.post(self.url, {
            'phone_number': self.valid_phone,
            'otp_code': "12345"  # Too short
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UserProfileAPITest(APITestCase):
    """Test cases for user profile API"""
    
    def setUp(self):
        self.url = reverse('users:user_profile')
        self.user = User.objects.create_user(
            username="testuser",
            phone_number="+1234567890",
            first_name="John",
            last_name="Doe"
        )
    
    def test_user_profile_get_authenticated(self):
        """Test getting user profile when authenticated"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['phone_number'], self.user.phone_number)
    
    def test_user_profile_get_unauthenticated(self):
        """Test getting user profile when not authenticated"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # DRF returns 'detail' instead of 'error' for auth errors
        self.assertTrue('detail' in response.data or 'error' in response.data)
    
    def test_user_profile_update_authenticated(self):
        """Test updating user profile when authenticated"""
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com'
        }
        
        response = self.client.patch(self.url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.last_name, 'Smith')
        self.assertEqual(self.user.email, 'jane.smith@example.com')
    
    def test_user_profile_update_unauthenticated(self):
        """Test updating user profile when not authenticated"""
        response = self.client.patch(self.url, {'first_name': 'Jane'})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_profile_invalid_email(self):
        """Test updating user profile with invalid email"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.patch(self.url, {'email': 'invalid-email'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_profile_jwt_token_authentication(self):
        """Test user profile access with JWT token"""
        # Generate JWT token
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        # Use JWT token for authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['phone_number'], self.user.phone_number)
