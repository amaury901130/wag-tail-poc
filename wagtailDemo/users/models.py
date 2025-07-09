from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        
    """Custom user model with phone-based authentication"""
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        help_text="User role in the system"
    )
    
    def __str__(self):
        return self.phone_number or self.username

    @property
    def is_moderator(self):
        """Check if user is a moderator."""
        return self.role == self.Role.MODERATOR
    
    @property
    def is_admin_user(self):
        """Check if user is an admin (different from Django's is_staff)."""
        return self.role == self.Role.ADMIN
    
    @property
    def is_regular_user(self):
        """Check if user is a regular user."""
        return self.role == self.Role.USER

    def save(self, *args, **kwargs):
        """Override save to set Django permissions based on role."""
        # Set Django staff status for admins and moderators to access Wagtail panel
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.MODERATOR:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False
        
        super().save(*args, **kwargs)

class OTPCode(models.Model):
    """Model to store OTP codes for authentication"""
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            # OTP expires in 5 minutes
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_code():
        """Generate a 6-digit OTP code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save()
    
    def __str__(self):
        return f"OTP for {self.phone_number}: {self.code}"
