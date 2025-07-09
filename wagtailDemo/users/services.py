"""
Mocked external OTP service for development/testing purposes.
In production, this would integrate with real SMS providers like Twilio, AWS SNS, etc.

This service follows Django best practices:
- Proper error handling and logging
- Clean separation of concerns
- Testable design
- Production-ready patterns
"""
import logging
import random
import re
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSServiceError(Exception):
    """Custom exception for SMS service errors"""
    pass


class MockedOTPService:
    """
    Mocked OTP service that simulates sending SMS codes.
    In development, it just logs the code instead of actually sending SMS.
    
    This service is designed to be easily replaceable with real SMS providers
    in production environments.
    """
    
    # Configuration constants
    FAILURE_RATE = 0.05  # 5% failure rate for testing
    PHONE_REGEX = re.compile(r'^\+?1?\d{9,14}$')  # Max 14 digits after optional +1
    
    def send_otp(self, phone_number: str, code: str) -> bool:
        """
        Send OTP via SMS (mocked implementation).
        
        Args:
            phone_number: The recipient's phone number
            code: The OTP code to send
            
        Returns:
            bool: True if sent successfully, False otherwise
            
        Raises:
            SMSServiceError: If there's a critical error
        """
        if not self.is_valid_phone_number(phone_number):
            logger.error(f"Invalid phone number format: {phone_number}")
            raise SMSServiceError(f"Invalid phone number format: {phone_number}")
        
        if not code or len(code) != 6 or not code.isdigit():
            logger.error(f"Invalid OTP code format: {code}")
            raise SMSServiceError(f"Invalid OTP code format: {code}")
        
        try:
            # In a real implementation, you would:
            # 1. Integrate with SMS provider (Twilio, AWS SNS, etc.)
            # 2. Send actual SMS
            # 3. Handle provider-specific errors
            # 4. Implement retry logic
            # 5. Track delivery status
            
            logger.info(f"[MOCKED SMS] Sending OTP {code} to {phone_number}")
            
            # Only print in development mode
            if settings.DEBUG:
                print(f"🚀 MOCKED SMS SERVICE: OTP {code} sent to {phone_number}")
            
            # Simulate occasional failures for testing
            if random.random() < self.FAILURE_RATE:
                logger.warning(f"[MOCKED SMS] Simulated failure for {phone_number}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"[MOCKED SMS] Error sending OTP to {phone_number}: {str(e)}")
            raise SMSServiceError(f"Failed to send OTP: {str(e)}")
    
    def is_valid_phone_number(self, phone_number: str) -> bool:
        """
        Validate if phone number is in correct format for the SMS provider.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            bool: True if valid format, False otherwise
        """
        if not phone_number:
            return False
        
        # Use class-level compiled regex for better performance
        return bool(self.PHONE_REGEX.match(phone_number))
    
    def get_supported_countries(self) -> list:
        """
        Get list of supported country codes.
        
        Returns:
            list: List of supported country codes
        """
        # In production, this would return actual supported countries
        # based on your SMS provider's capabilities
        return ['+1']  # Currently only supports North America
    
    def format_phone_number(self, phone_number: str) -> Optional[str]:
        """
        Format phone number to standard international format.
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            str: Formatted phone number or None if invalid
        """
        if not phone_number:
            return None
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # Add +1 prefix if missing (North America)
        if not cleaned.startswith('+'):
            if cleaned.startswith('1') and len(cleaned) == 11:
                # Already has country code
                cleaned = '+' + cleaned
            else:
                # Add country code
                cleaned = '+1' + cleaned
        
        return cleaned if self.is_valid_phone_number(cleaned) else None


class RealSMSService(MockedOTPService):
    """
    Real SMS service implementation for production.
    Extend this class to integrate with actual SMS providers.
    """
    
    def __init__(self, api_key: str, api_secret: str, provider: str = 'twilio'):
        """
        Initialize real SMS service with provider credentials.
        
        Args:
            api_key: SMS provider API key
            api_secret: SMS provider API secret
            provider: SMS provider name ('twilio', 'aws_sns', etc.)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.provider = provider
        # Initialize provider-specific client here
    
    def send_otp(self, phone_number: str, code: str) -> bool:
        """
        Send OTP via real SMS provider.
        Override this method with actual SMS provider integration.
        """
        # TODO: Implement actual SMS provider integration
        # For now, fall back to mocked behavior
        logger.warning("Real SMS service not implemented, falling back to mocked service")
        return super().send_otp(phone_number, code)


# Factory function to get appropriate SMS service
def get_sms_service() -> MockedOTPService:
    """
    Factory function to get the appropriate SMS service instance.
    
    Returns:
        MockedOTPService: SMS service instance
    """
    # In production, you would check environment variables
    # to determine which SMS service to use
    if getattr(settings, 'USE_REAL_SMS_SERVICE', False):
        api_key = getattr(settings, 'SMS_API_KEY', None)
        api_secret = getattr(settings, 'SMS_API_SECRET', None)
        provider = getattr(settings, 'SMS_PROVIDER', 'twilio')
        
        if api_key and api_secret:
            return RealSMSService(api_key, api_secret, provider)
    
    # Default to mocked service
    return MockedOTPService()


# Singleton instance - use factory function
otp_service = get_sms_service()
