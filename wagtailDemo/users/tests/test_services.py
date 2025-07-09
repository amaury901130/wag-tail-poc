from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.conf import settings

from ..services import MockedOTPService, RealSMSService, get_sms_service, SMSServiceError


class MockedOTPServiceTest(TestCase):
    """Test cases for the mocked OTP service"""
    
    def setUp(self):
        """Set up test instances"""
        self.service = MockedOTPService()
    
    def test_send_otp_success(self):
        """Test successful OTP sending"""
        with patch('random.random', return_value=0.9):  # Ensure no failure
            result = self.service.send_otp("+1234567890", "123456")
            self.assertTrue(result)
    
    def test_send_otp_random_failure(self):
        """Test random failure simulation"""
        with patch('random.random', return_value=0.01):  # Force failure
            result = self.service.send_otp("+1234567890", "123456")
            self.assertFalse(result)
    
    def test_send_otp_invalid_phone_number(self):
        """Test sending OTP with invalid phone number"""
        with self.assertRaises(SMSServiceError):
            self.service.send_otp("invalid", "123456")
    
    def test_send_otp_invalid_code(self):
        """Test sending OTP with invalid code"""
        with self.assertRaises(SMSServiceError):
            self.service.send_otp("+1234567890", "12345")  # Too short
        
        with self.assertRaises(SMSServiceError):
            self.service.send_otp("+1234567890", "12345a")  # Contains letter
    
    def test_is_valid_phone_number_valid(self):
        """Test phone number validation with valid numbers"""
        valid_numbers = [
            "+1234567890",
            "1234567890",
            "+12345678901234",  # Max 14 digits
        ]
        
        for phone in valid_numbers:
            with self.subTest(phone=phone):
                self.assertTrue(self.service.is_valid_phone_number(phone))
    
    def test_is_valid_phone_number_invalid(self):
        """Test phone number validation with invalid numbers"""
        invalid_numbers = [
            "123",  # Too short
            "+1234567890123456",  # Too long
            "abc123def456",  # Contains letters
            "+1-234-567-890",  # Contains dashes
            "",  # Empty
            None,  # None
        ]
        
        for phone in invalid_numbers:
            with self.subTest(phone=phone):
                self.assertFalse(self.service.is_valid_phone_number(phone))
    
    def test_format_phone_number(self):
        """Test phone number formatting"""
        test_cases = [
            ("1234567890", "+11234567890"),  # 10 digits -> add +1
            ("+1234567890", "+1234567890"),  # Already has +
            ("11234567890", "+11234567890"), # 11 digits starting with 1
            ("(123) 456-7890", "+11234567890"), # Formatted phone
            ("123-456-7890", "+11234567890"), # Dashed phone
            ("", None),
            ("invalid", None),
        ]
        
        for input_phone, expected in test_cases:
            with self.subTest(input_phone=input_phone):
                result = self.service.format_phone_number(input_phone)
                self.assertEqual(result, expected)
    
    def test_get_supported_countries(self):
        """Test getting supported countries"""
        countries = self.service.get_supported_countries()
        self.assertIsInstance(countries, list)
        self.assertIn('+1', countries)
    
    def test_send_otp_with_exception(self):
        """Test OTP sending with exception handling"""
        # Mock the random module to ensure no random failure
        with patch('wagtailDemo.users.services.random.random', return_value=0.9):
            # Mock settings.DEBUG to True to trigger print statement
            with patch('wagtailDemo.users.services.settings.DEBUG', True):
                with patch('builtins.print', side_effect=Exception("Test exception")):
                    # This should raise SMSServiceError due to the exception
                    with self.assertRaises(SMSServiceError):
                        self.service.send_otp("+1234567890", "123456")


class RealSMSServiceTest(TestCase):
    """Test cases for the real SMS service"""
    
    def test_initialization(self):
        """Test service initialization"""
        service = RealSMSService("test_key", "test_secret", "twilio")
        self.assertEqual(service.api_key, "test_key")
        self.assertEqual(service.api_secret, "test_secret")
        self.assertEqual(service.provider, "twilio")
    
    def test_send_otp_fallback(self):
        """Test that send_otp falls back to mocked behavior"""
        service = RealSMSService("test_key", "test_secret", "twilio")
        
        with patch('random.random', return_value=0.9):  # Ensure no failure
            result = service.send_otp("+1234567890", "123456")
            self.assertTrue(result)


class SMSServiceFactoryTest(TestCase):
    """Test cases for the SMS service factory"""
    
    def test_get_sms_service_default(self):
        """Test getting default mocked service"""
        service = get_sms_service()
        self.assertIsInstance(service, MockedOTPService)
    
    @patch('wagtailDemo.users.services.settings')
    def test_get_sms_service_real(self, mock_settings):
        """Test getting real SMS service when configured"""
        mock_settings.USE_REAL_SMS_SERVICE = True
        mock_settings.SMS_API_KEY = 'test_key'
        mock_settings.SMS_API_SECRET = 'test_secret'
        mock_settings.SMS_PROVIDER = 'twilio'
        
        service = get_sms_service()
        self.assertIsInstance(service, RealSMSService)
        self.assertEqual(service.api_key, 'test_key')
        self.assertEqual(service.api_secret, 'test_secret')
        self.assertEqual(service.provider, 'twilio')
    
    @patch('wagtailDemo.users.services.settings')
    def test_get_sms_service_real_missing_credentials(self, mock_settings):
        """Test fallback to mocked service when real service credentials are missing"""
        mock_settings.USE_REAL_SMS_SERVICE = True
        mock_settings.SMS_API_KEY = None
        mock_settings.SMS_API_SECRET = None
        
        service = get_sms_service()
        self.assertIsInstance(service, MockedOTPService)
