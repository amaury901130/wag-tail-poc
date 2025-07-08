from django.test import TestCase
from ..serializers import SendOTPSerializer, VerifyOTPSerializer, UserSerializer
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
