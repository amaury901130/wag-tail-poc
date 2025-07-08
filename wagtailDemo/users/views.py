from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from .models import OTPCode
from .serializers import SendOTPSerializer, VerifyOTPSerializer, UserSerializer
from .services import otp_service

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """
    Send OTP code to phone number.
    Creates a new OTP record and sends it via mocked SMS service.
    """
    serializer = SendOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    phone_number = serializer.validated_data['phone_number']
    
    try:
        with transaction.atomic():
            # Invalidate any existing unused OTP codes for this phone number
            OTPCode.objects.filter(
                phone_number=phone_number,
                is_used=False
            ).update(is_used=True)
            
            # Create new OTP
            otp_record = OTPCode.objects.create(phone_number=phone_number)
            
            # Send OTP via mocked service
            if otp_service.send_otp(phone_number, otp_record.code):
                return Response({
                    'message': 'OTP sent successfully',
                    'phone_number': phone_number,
                    'expires_in_minutes': 5
                }, status=status.HTTP_200_OK)
            else:
                # If sending fails, mark OTP as used to prevent abuse
                otp_record.mark_as_used()
                return Response(
                    {'error': 'Failed to send OTP. Please try again.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP code and login/signup user.
    If user doesn't exist, create a new one.
    Returns JWT tokens for authentication.
    """
    serializer = VerifyOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    phone_number = serializer.validated_data['phone_number']
    otp_code = serializer.validated_data['otp_code']
    
    try:
        with transaction.atomic():
            # Find the most recent valid OTP for this phone number
            otp_record = OTPCode.objects.filter(
                phone_number=phone_number,
                code=otp_code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if not otp_record:
                return Response(
                    {'error': 'Invalid or expired OTP code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark OTP as used
            otp_record.mark_as_used()
            
            # Get or create user
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'username': phone_number,  # Use phone as username
                    'is_phone_verified': True
                }
            )
            
            # If user already exists but phone wasn't verified, verify it now
            if not created and not user.is_phone_verified:
                user.is_phone_verified = True
                user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Serialize user data
            user_data = UserSerializer(user).data
            
            return Response({
                'message': 'Authentication successful',
                'user': user_data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                },
                'is_new_user': created
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def user_profile(request):
    """
    Get current user profile.
    Requires authentication.
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user_data = UserSerializer(request.user).data
    return Response({
        'user': user_data
    }, status=status.HTTP_200_OK)
