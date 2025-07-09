from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import OTPCode
from .services import otp_service
import re

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    """
    Serializer for sending OTP to phone number.
    Validates phone number format and provides detailed error messages.
    """
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number in international format (e.g., +1234567890)"
    )
    
    def validate_phone_number(self, value):
        """
        Validate phone number format using the SMS service validator.
        
        Args:
            value: Phone number string
            
        Returns:
            str: Validated and formatted phone number
            
        Raises:
            ValidationError: If phone number is invalid
        """
        if not value:
            raise serializers.ValidationError("Phone number is required")
        
        # Use the service's validation logic
        if not otp_service.is_valid_phone_number(value):
            raise serializers.ValidationError(
                "Invalid phone number format. Please use international format (e.g., +1234567890)"
            )
        
        # Format the phone number
        formatted_number = otp_service.format_phone_number(value)
        if not formatted_number:
            raise serializers.ValidationError("Unable to format phone number")
        
        return formatted_number
    
    def validate(self, attrs):
        """
        Validate the entire serializer data.
        
        Args:
            attrs: Dictionary of validated field data
            
        Returns:
            dict: Validated data
        """
        phone_number = attrs.get('phone_number')
        
        # Check if phone number is supported
        supported_countries = otp_service.get_supported_countries()
        if not any(phone_number.startswith(code) for code in supported_countries):
            raise serializers.ValidationError({
                'phone_number': f'Phone number must start with one of: {", ".join(supported_countries)}'
            })
        
        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying OTP and login/signup.
    Validates both phone number and OTP code format.
    """
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number in international format (e.g., +1234567890)"
    )
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text="6-digit OTP code"
    )
    
    def validate_phone_number(self, value):
        """
        Validate phone number format using the SMS service validator.
        
        Args:
            value: Phone number string
            
        Returns:
            str: Validated and formatted phone number
            
        Raises:
            ValidationError: If phone number is invalid
        """
        if not value:
            raise serializers.ValidationError("Phone number is required")
        
        # Use the service's validation logic
        if not otp_service.is_valid_phone_number(value):
            raise serializers.ValidationError(
                "Invalid phone number format. Please use international format (e.g., +1234567890)"
            )
        
        # Format the phone number
        formatted_number = otp_service.format_phone_number(value)
        if not formatted_number:
            raise serializers.ValidationError("Unable to format phone number")
        
        return formatted_number
    
    def validate_otp_code(self, value):
        """
        Validate OTP code format.
        
        Args:
            value: OTP code string
            
        Returns:
            str: Validated OTP code
            
        Raises:
            ValidationError: If OTP code is invalid
        """
        if not value:
            raise serializers.ValidationError("OTP code is required")
        
        if len(value) != 6:
            raise serializers.ValidationError("OTP code must be exactly 6 digits")
        
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must contain only digits")
        
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Handles user profile data with proper validation.
    """
    class Meta:
        model = User
        fields = [
            'id', 
            'phone_number', 
            'username', 
            'first_name', 
            'last_name', 
            'email',
            'is_phone_verified', 
            'date_joined',
            'last_login'
        ]
        read_only_fields = [
            'id', 
            'username', 
            'phone_number',
            'is_phone_verified', 
            'date_joined',
            'last_login'
        ]
    
    def validate_email(self, value):
        """
        Validate email format if provided.
        
        Args:
            value: Email string
            
        Returns:
            str: Validated email
            
        Raises:
            ValidationError: If email is invalid
        """
        if value and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format")
        
        return value
    
    def validate_first_name(self, value):
        """
        Validate first name if provided.
        
        Args:
            value: First name string
            
        Returns:
            str: Validated first name
            
        Raises:
            ValidationError: If first name is invalid
        """
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters")
        
        return value.strip() if value else value
    
    def validate_last_name(self, value):
        """
        Validate last name if provided.
        
        Args:
            value: Last name string
            
        Returns:
            str: Validated last name
            
        Raises:
            ValidationError: If last name is invalid
        """
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters")
        
        return value.strip() if value else value


class UserProfileUpdateSerializer(UserSerializer):
    """
    Serializer for updating user profile.
    Extends UserSerializer with additional validation for profile updates.
    """
    def validate(self, attrs):
        """
        Validate the entire profile update data.
        
        Args:
            attrs: Dictionary of validated field data
            
        Returns:
            dict: Validated data
        """
        # Ensure at least one field is being updated
        updatable_fields = ['first_name', 'last_name', 'email']
        if not any(field in attrs for field in updatable_fields):
            raise serializers.ValidationError(
                "At least one field must be provided for update"
            )
        
        return attrs
