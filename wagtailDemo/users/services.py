"""
Mocked external OTP service for development/testing purposes.
In production, this would integrate with real SMS providers like Twilio, AWS SNS, etc.
"""
import logging

logger = logging.getLogger(__name__)


class MockedOTPService:
    """
    Mocked OTP service that simulates sending SMS codes.
    In development, it just logs the code instead of actually sending SMS.
    """
    
    @staticmethod
    def send_otp(phone_number: str, code: str) -> bool:
        """
        Mock function to send OTP via SMS.
        
        Args:
            phone_number: The recipient's phone number
            code: The OTP code to send
            
        Returns:
            bool: True if "sent" successfully, False otherwise
        """
        try:
            # In a real implementation, you would:
            # 1. Integrate with SMS provider (Twilio, AWS SNS, etc.)
            # 2. Send actual SMS
            # 3. Handle provider-specific errors
            
            # For now, we just log it
            logger.info(f"[MOCKED SMS] Sending OTP {code} to {phone_number}")
            print(f"🚀 MOCKED SMS SERVICE: OTP {code} sent to {phone_number}")
            
            # Simulate occasional failures (5% failure rate for testing)
            import random
            if random.random() < 0.05:
                logger.error(f"[MOCKED SMS] Failed to send OTP to {phone_number}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"[MOCKED SMS] Error sending OTP to {phone_number}: {str(e)}")
            return False
    
    @staticmethod
    def is_valid_phone_number(phone_number: str) -> bool:
        """
        Validate if phone number is in correct format for the SMS provider.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            bool: True if valid format, False otherwise
        """
        import re
        # Basic validation - in production you might want more sophisticated validation
        phone_regex = re.compile(r'^\+?1?\d{9,14}$')  # Max 14 digits after optional +1
        return bool(phone_regex.match(phone_number))


# Singleton instance
otp_service = MockedOTPService()
