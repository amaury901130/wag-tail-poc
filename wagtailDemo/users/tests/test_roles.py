from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserRoleModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'phone_number': '+1234567890',
            'username': 'testuser',
            'is_phone_verified': True
        }

    def test_user_default_role(self):
        """Test that new users get default role."""
        user = User.objects.create(**self.user_data)
        self.assertEqual(user.role, User.Role.USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_admin_role_permissions(self):
        """Test that admin role sets correct permissions."""
        user = User.objects.create(role=User.Role.ADMIN, **self.user_data)
        self.assertTrue(user.is_admin_user)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_moderator_role_permissions(self):
        """Test that moderator role sets correct permissions."""
        user = User.objects.create(role=User.Role.MODERATOR, **self.user_data)
        self.assertTrue(user.is_moderator)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_role_properties(self):
        """Test role-checking properties."""
        user = User.objects.create(role=User.Role.USER, **self.user_data)
        self.assertTrue(user.is_regular_user)
        self.assertFalse(user.is_moderator)
        self.assertFalse(user.is_admin_user)

class RoleAPITest(APITestCase):
    def setUp(self):
        # Create test users with different roles
        self.admin_user = User.objects.create(
            phone_number='+1111111111',
            username='admin',
            role=User.Role.ADMIN,
            is_phone_verified=True
        )
        
        self.moderator_user = User.objects.create(
            phone_number='+2222222222',
            username='moderator',
            role=User.Role.MODERATOR,
            is_phone_verified=True
        )
        
        self.regular_user = User.objects.create(
            phone_number='+3333333333',
            username='user',
            role=User.Role.USER,
            is_phone_verified=True
        )

    def test_user_list_admin_only(self):
        """Test that only admins can list users."""
        # Admin can access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/auth/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Moderator cannot access
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.get('/api/auth/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Regular user cannot access
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/auth/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_role_update_admin_only(self):
        """Test that only admins can update user roles."""
        url = f'/api/auth/users/{self.regular_user.id}/role/'
        data = {'role': User.Role.MODERATOR}
        
        # Admin can update
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.role, User.Role.MODERATOR)
        
        # Moderator cannot update
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_remove_own_role(self):
        """Test that admin cannot remove their own admin role."""
        url = f'/api/auth/users/{self.admin_user.id}/role/'
        data = {'role': User.Role.USER}
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot remove your own admin role', response.data['error'])

    def test_role_display_in_profile(self):
        """Test that role information is included in user profile."""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], User.Role.MODERATOR)
        self.assertEqual(response.data['role_display'], 'Moderator')