from django.test import TestCase
from unittest.mock import patch

from ..services import MockedOTPService, otp_service


class MockedOTPServiceTest(TestCase):
    """Test cases for the mocked OTP service"""
    
    def test_send_otp_success(self):
        """Test successful OTP sending"""
        with patch('random.random', return_value=0.9):  # Ensure no failure
            result = otp_service.send_otp("+1234567890", "123456")
            self.assertTrue(result)
    
    def test_send_otp_random_failure(self):
        """Test random failure simulation"""
        with patch('random.random', return_value=0.01):  # Force failure
            result = otp_service.send_otp("+1234567890", "123456")
            self.assertFalse(result)
    
    def test_is_valid_phone_number_valid(self):
        """Test phone number validation with valid numbers"""
        valid_numbers = [
            "+1234567890",
            "1234567890",
            "+12345678901234",  # Max 14 digits
        ]
        
        for phone in valid_numbers:
            with self.subTest(phone=phone):
                self.assertTrue(otp_service.is_valid_phone_number(phone))
    
    def test_is_valid_phone_number_invalid(self):
        """Test phone number validation with invalid numbers"""
        invalid_numbers = [
            "123",  # Too short
            "+1234567890123456",  # Too long
            "abc123def456",  # Contains letters
            "+1-234-567-890",  # Contains dashes
            "",  # Empty
        ]
        
        for phone in invalid_numbers:
            with self.subTest(phone=phone):
                self.assertFalse(otp_service.is_valid_phone_number(phone))
    
    def test_send_otp_with_exception(self):
        """Test OTP sending with exception handling"""
        with patch('builtins.print', side_effect=Exception("Test exception")):
            result = otp_service.send_otp("+1234567890", "123456")
            self.assertFalse(result)
