from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from ..models import OTPCode

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def test_user_creation_with_phone(self):
        """Test creating user with phone number"""
        user = User.objects.create_user(
            username="testuser",
            phone_number="+1234567890"
        )
        self.assertEqual(user.phone_number, "+1234567890")
        self.assertFalse(user.is_phone_verified)
    
    def test_user_str_representation(self):
        """Test string representation of user"""
        user = User.objects.create_user(
            username="testuser",
            phone_number="+1234567890"
        )
        self.assertEqual(str(user), "+1234567890")
        
        user_without_phone = User.objects.create_user(
            username="testuser2"
        )
        self.assertEqual(str(user_without_phone), "testuser2")


class OTPCodeModelTest(TestCase):
    """Test cases for OTPCode model"""
    
    def test_otp_creation(self):
        """Test OTP code creation"""
        otp = OTPCode.objects.create(phone_number="+1234567890")
        
        self.assertEqual(otp.phone_number, "+1234567890")
        self.assertEqual(len(otp.code), 6)
        self.assertTrue(otp.code.isdigit())
        self.assertFalse(otp.is_used)
        self.assertTrue(otp.is_valid())
    
    def test_otp_expiration(self):
        """Test OTP expiration"""
        # Create expired OTP
        otp = OTPCode.objects.create(
            phone_number="+1234567890",
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        
        self.assertFalse(otp.is_valid())
    
    def test_otp_used_flag(self):
        """Test OTP used flag"""
        otp = OTPCode.objects.create(phone_number="+1234567890")
        
        self.assertTrue(otp.is_valid())
        
        otp.mark_as_used()
        self.assertFalse(otp.is_valid())
        self.assertTrue(otp.is_used)
    
    def test_otp_code_generation(self):
        """Test OTP code generation"""
        code = OTPCode.generate_code()
        
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
    
    def test_otp_str_representation(self):
        """Test string representation of OTP"""
        otp = OTPCode.objects.create(phone_number="+1234567890")
        expected_str = f"OTP for +1234567890: {otp.code}"
        self.assertEqual(str(otp), expected_str)
