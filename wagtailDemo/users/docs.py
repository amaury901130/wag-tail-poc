from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def api_documentation(request):
    """
    API documentation for OTP authentication system.
    """
    docs = {
        "title": "OTP Authentication API",
        "version": "1.0.0",
        "description": "Phone-based authentication using One-Time Passwords (OTP)",
        "base_url": request.build_absolute_uri('/'),
        "endpoints": {
            "send_otp": {
                "url": "/api/auth/send-otp/",
                "method": "POST",
                "description": "Send OTP code to phone number",
                "request_body": {
                    "phone_number": "string (required) - Phone number in international format"
                },
                "responses": {
                    "200": {
                        "message": "OTP sent successfully",
                        "phone_number": "+1234567890",
                        "expires_in_minutes": 5
                    },
                    "400": {
                        "error": "Invalid data",
                        "details": {"phone_number": ["Invalid phone number format"]}
                    },
                    "500": {
                        "error": "Failed to send OTP. Please try again."
                    }
                }
            },
            "verify_otp": {
                "url": "/api/auth/verify-otp/",
                "method": "POST",
                "description": "Verify OTP code and authenticate user",
                "request_body": {
                    "phone_number": "string (required) - Phone number",
                    "otp_code": "string (required) - 6-digit OTP code"
                },
                "responses": {
                    "200": {
                        "message": "Authentication successful",
                        "user": {
                            "id": 1,
                            "phone_number": "+1234567890",
                            "username": "+1234567890",
                            "first_name": "",
                            "last_name": "",
                            "is_phone_verified": True,
                            "date_joined": "2025-07-08T12:34:56Z"
                        },
                        "tokens": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        },
                        "is_new_user": True
                    },
                    "400": {
                        "error": "Invalid or expired OTP code"
                    }
                }
            },
            "user_profile": {
                "url": "/api/auth/profile/",
                "method": "GET",
                "description": "Get current user profile (requires authentication)",
                "headers": {
                    "Authorization": "Bearer <access_token>"
                },
                "responses": {
                    "200": {
                        "user": {
                            "id": 1,
                            "phone_number": "+1234567890",
                            "username": "+1234567890",
                            "first_name": "",
                            "last_name": "",
                            "is_phone_verified": True,
                            "date_joined": "2025-07-08T12:34:56Z"
                        }
                    },
                    "401": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            }
        },
        "authentication": {
            "type": "JWT Bearer Token",
            "description": "Include 'Authorization: Bearer <token>' header for authenticated endpoints",
            "token_lifetime": {
                "access": "24 hours",
                "refresh": "7 days"
            }
        },
        "phone_number_format": {
            "description": "Phone numbers should be in international format",
            "examples": ["+1234567890", "+44123456789", "+33123456789"],
            "validation": "Must contain 9-14 digits after optional country code"
        },
        "otp_details": {
            "code_length": 6,
            "expiry_time": "5 minutes",
            "single_use": True,
            "note": "Sending new OTP invalidates previous codes for the same phone number"
        }
    }
    
    return Response(docs, status=status.HTTP_200_OK)
