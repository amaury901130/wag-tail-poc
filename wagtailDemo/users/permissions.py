"""
Custom permissions for the users app.
Following Django REST Framework best practices for permission handling.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the profile
        return obj == request.user


class IsPhoneVerified(permissions.BasePermission):
    """
    Custom permission to only allow phone verified users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and hasattr(request.user, 'is_phone_verified') 
            and request.user.is_phone_verified
        )


class IsProfileOwner(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own profile.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsSameUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow users to modify their own data,
    or read-only access to other users' public data.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for the same user
        return obj == request.user
