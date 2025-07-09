from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.conf import settings
import logging

from .models import OTPCode
from .serializers import SendOTPSerializer, VerifyOTPSerializer, UserSerializer, UserProfileUpdateSerializer
from .services import otp_service, SMSServiceError
from .permissions import IsProfileOwner, IsAdminRole, CanManageUsers

from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, UserProfileSerializer, 
    UserProfileUpdateSerializer, UserRoleUpdateSerializer
)

logger = logging.getLogger(__name__)
User = get_user_model()


class SendOTPView(APIView):
    """
    Send OTP code to phone number.
    Creates a new OTP record and sends it via SMS service.
    """
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer
    
    def post(self, request):
        """
        Handle OTP sending request.
        
        Returns:
            Response: Success with OTP details or error message
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid data',
                    'details': serializer.errors
                },
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
                
                # Send OTP via SMS service
                if otp_service.send_otp(phone_number, otp_record.code):
                    logger.info(f"OTP sent successfully to {phone_number}")
                    return Response({
                        'message': 'OTP sent successfully',
                        'phone_number': phone_number,
                        'expires_in_minutes': 5
                    }, status=status.HTTP_200_OK)
                else:
                    # If sending fails, mark OTP as used to prevent abuse
                    otp_record.mark_as_used()
                    logger.warning(f"Failed to send OTP to {phone_number}")
                    return Response(
                        {'error': 'Failed to send OTP. Please try again.'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                    
        except SMSServiceError as e:
            logger.error(f"SMS service error for {phone_number}: {str(e)}")
            return Response(
                {'error': 'SMS service error. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Unexpected error sending OTP to {phone_number}: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyOTPView(APIView):
    """
    Verify OTP code and login/signup user.
    If user doesn't exist, create a new one.
    Returns JWT tokens for authentication.
    """
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer
    
    def post(self, request):
        """
        Handle OTP verification request.
        
        Returns:
            Response: Success with user data and tokens or error message
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid data',
                    'details': serializer.errors
                },
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
                    logger.warning(f"Invalid OTP attempt for {phone_number}")
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
                
                logger.info(f"User {'created' if created else 'logged in'}: {phone_number}")
                
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
            logger.error(f"Unexpected error verifying OTP for {phone_number}: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(RetrieveUpdateAPIView):
    """
    Get and update current user profile.
    Uses JWT authentication with custom permissions.
    """
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsProfileOwner]
    
    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on request method."""
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def get(self, request, *args, **kwargs):
        """Get current user profile."""
        user_data = UserProfileSerializer(request.user).data
        return Response(user_data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        """Update user profile."""
        return self.update(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        """Partially update user profile."""
        return self.partial_update(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Override update to provide custom response format."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_user = serializer.save()
        
        # Return updated user data
        user_data = UserSerializer(updated_user).data
        return Response({
            'message': 'Profile updated successfully',
            'user': user_data
        }, status=status.HTTP_200_OK)

class UserListView(generics.ListAPIView):
    """List all users (Admin only)."""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

class UserRoleUpdateView(generics.UpdateAPIView):
    """Update user role (Admin only)."""
    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Prevent admin from removing their own admin role
            if user == request.user and serializer.validated_data.get('role') != User.Role.ADMIN:
                return Response({
                    'error': 'You cannot remove your own admin role'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({
                'message': f'User role updated to {user.get_role_display()}',
                'user': UserProfileSerializer(user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Keep backward compatibility - create view instances
send_otp = SendOTPView.as_view()
verify_otp = VerifyOTPView.as_view()
user_profile = UserProfileView.as_view()
user_list = UserListView.as_view()
user_role_update = UserRoleUpdateView.as_view()
