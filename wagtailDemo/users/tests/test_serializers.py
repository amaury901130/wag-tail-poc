from django.test import TestCase
from unittest.mock import patch
from ..serializers import (
    SendOTPSerializer, 
    VerifyOTPSerializer, 
    UserSerializer,
    UserProfileUpdateSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()


class SendOTPSerializerTest(TestCase):
    """Test cases for SendOTPSerializer"""
    
    def test_valid_phone_numbers(self):
        """Test serializer with valid phone numbers"""
        valid_phones = [
            "+1234567890",
            "1234567890",
            "+12345678901234",  # Max 14 digits
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                serializer = SendOTPSerializer(data={'phone_number': phone})
                self.assertTrue(serializer.is_valid(), f"Phone {phone} should be valid")
    
    def test_invalid_phone_numbers(self):
        """Test serializer with invalid phone numbers"""
        invalid_phones = [
            "123",  # Too short
            "+1234567890123456",  # Too long
            "abc123def456",  # Contains letters
            "",  # Empty
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                serializer = SendOTPSerializer(data={'phone_number': phone})
                self.assertFalse(serializer.is_valid(), f"Phone {phone} should be invalid")
    
    def test_phone_number_formatting(self):
        """Test that phone numbers are formatted correctly"""
        with patch('wagtailDemo.users.services.otp_service.format_phone_number') as mock_format:
            mock_format.return_value = "+11234567890"
            
            serializer = SendOTPSerializer(data={'phone_number': '1234567890'})
            self.assertTrue(serializer.is_valid())
            self.assertEqual(serializer.validated_data['phone_number'], '+11234567890')
    
    def test_unsupported_country_code(self):
        """Test validation fails for unsupported country codes"""
        with patch('wagtailDemo.users.services.otp_service.get_supported_countries') as mock_supported:
            mock_supported.return_value = ['+1']
            
            serializer = SendOTPSerializer(data={'phone_number': '+44123456789'})
            self.assertFalse(serializer.is_valid())
            # The error should be in phone_number field, not non_field_errors
            self.assertIn('phone_number', serializer.errors)


class VerifyOTPSerializerTest(TestCase):
    """Test cases for VerifyOTPSerializer"""
    
    def test_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'phone_number': '+1234567890',
            'otp_code': '123456'
        }
        serializer = VerifyOTPSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_otp_code_length(self):
        """Test serializer with invalid OTP code length"""
        invalid_codes = ['12345', '1234567', '']
        
        for code in invalid_codes:
            with self.subTest(code=code):
                data = {
                    'phone_number': '+1234567890',
                    'otp_code': code
                }
                serializer = VerifyOTPSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn('otp_code', serializer.errors)
    
    def test_invalid_otp_code_format(self):
        """Test serializer with invalid OTP code format"""
        invalid_codes = ['12345a', 'abcdef', '12-345']
        
        for code in invalid_codes:
            with self.subTest(code=code):
                data = {
                    'phone_number': '+1234567890',
                    'otp_code': code
                }
                serializer = VerifyOTPSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn('otp_code', serializer.errors)
    
    def test_phone_number_formatting(self):
        """Test that phone numbers are formatted correctly"""
        with patch('wagtailDemo.users.services.otp_service.format_phone_number') as mock_format:
            mock_format.return_value = "+11234567890"
            
            serializer = VerifyOTPSerializer(data={
                'phone_number': '1234567890',
                'otp_code': '123456'
            })
            self.assertTrue(serializer.is_valid())
            self.assertEqual(serializer.validated_data['phone_number'], '+11234567890')
    
    def test_invalid_phone_number(self):
        """Test serializer with invalid phone number"""
        data = {
            'phone_number': 'invalid',
            'otp_code': '123456'
        }
        serializer = VerifyOTPSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
    
    def test_invalid_otp_code(self):
        """Test serializer with invalid OTP codes"""
        invalid_codes = [
            "12345",  # Too short
            "1234567",  # Too long
            "12345a",  # Contains letter
            "",  # Empty
        ]
        
        for code in invalid_codes:
            with self.subTest(code=code):
                data = {
                    'phone_number': '+1234567890',
                    'otp_code': code
                }
                serializer = VerifyOTPSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn('otp_code', serializer.errors)


class UserSerializerTest(TestCase):
    """Test cases for UserSerializer"""
    
    def test_user_serialization(self):
        """Test user serialization"""
        user = User.objects.create_user(
            username="testuser",
            phone_number="+1234567890",
            first_name="Test",
            last_name="User"
        )
        
        serializer = UserSerializer(user)
        data = serializer.data
        
        self.assertEqual(data['phone_number'], "+1234567890")
        self.assertEqual(data['username'], "testuser")
        self.assertEqual(data['first_name'], "Test")
        self.assertEqual(data['last_name'], "User")
        self.assertIn('id', data)
        self.assertIn('date_joined', data)
    
    def test_read_only_fields(self):
        """Test that read-only fields cannot be updated"""
        user = User.objects.create_user(
            username="testuser",
            phone_number="+1234567890"
        )
        
        # Try to update read-only fields
        data = {
            'id': 999,
            'username': 'hacker',
            'is_phone_verified': True,
            'first_name': 'Updated',  # This should work
        }
        
        serializer = UserSerializer(user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        
        # Read-only fields should not change
        self.assertNotEqual(updated_user.id, 999)
        self.assertEqual(updated_user.username, "testuser")
        
        # Writable fields should change
        self.assertEqual(updated_user.first_name, "Updated")
    
    def test_user_email_validation(self):
        """Test email validation"""
        invalid_emails = ['invalid-email', 'test@', '@example.com']
        
        for email in invalid_emails:
            with self.subTest(email=email):
                serializer = UserSerializer(data={'email': email})
                self.assertFalse(serializer.is_valid())
                self.assertIn('email', serializer.errors)
    
    def test_user_name_validation(self):
        """Test name validation"""
        # Test short names
        for field in ['first_name', 'last_name']:
            with self.subTest(field=field):
                serializer = UserSerializer(data={field: 'J'})
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)
    
    def test_valid_email_format(self):
        """Test valid email formats"""
        valid_emails = ['test@example.com', 'user.name@domain.co.uk', 'user+tag@example.org']
        
        for email in valid_emails:
            with self.subTest(email=email):
                serializer = UserSerializer(data={'email': email})
                self.assertTrue(serializer.is_valid())


class UserProfileUpdateSerializerTest(TestCase):
    """Test cases for UserProfileUpdateSerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            phone_number="+1234567890"
        )
    
    def test_valid_profile_update(self):
        """Test valid profile update"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com'
        }
        serializer = UserProfileUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_empty_profile_update(self):
        """Test that empty profile update fails validation"""
        serializer = UserProfileUpdateSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_partial_profile_update(self):
        """Test partial profile update"""
        data = {'first_name': 'John'}
        serializer = UserProfileUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_readonly_fields_not_updatable(self):
        """Test that readonly fields cannot be updated via profile update"""
        data = {
            'first_name': 'John',
            'phone_number': '+9876543210',  # Should be readonly
            'is_phone_verified': False  # Should be readonly
        }
        serializer = UserProfileUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Check that only allowed fields are in validated data
        validated_data = serializer.validated_data
        self.assertIn('first_name', validated_data)
        self.assertNotIn('phone_number', validated_data)
        self.assertNotIn('is_phone_verified', validated_data)
