from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTPCode
import re

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP to phone number"""
    phone_number = serializers.CharField(max_length=20)
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        # Basic phone number validation (you can make this more strict)
        phone_regex = re.compile(r'^\+?1?\d{9,14}$')  # Max 14 digits after optional +1
        if not phone_regex.match(value):
            raise serializers.ValidationError("Invalid phone number format")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP and login/signup"""
    phone_number = serializers.CharField(max_length=20)
    otp_code = serializers.CharField(max_length=6)
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        phone_regex = re.compile(r'^\+?1?\d{9,14}$')  # Max 14 digits after optional +1
        if not phone_regex.match(value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
    
    def validate_otp_code(self, value):
        """Validate OTP code format"""
        if len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("OTP code must be 6 digits")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'username', 'first_name', 'last_name', 'is_phone_verified', 'date_joined']
        read_only_fields = ['id', 'username', 'is_phone_verified', 'date_joined']
