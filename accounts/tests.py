from allauth.account.models import EmailAddress
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

User = get_user_model()


class ComprehensiveAccountTests(TestCase):

    def setUp(self):
        """
        Run before each test. Sets up a client and a user with a confirmed email.
        """
        self.client = APIClient()
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'a-very-strong-password-123!',
            'first_name': 'Test',
            'last_name': 'User',
        }
        self.user = User.objects.create_user(**self.user_data)

        EmailAddress.objects.create(
            user=self.user,
            email=self.user_data['email'],
            primary=True,
            verified=True
        )

    def test_user_creation_edge_cases(self):
        """Test edge cases for the CustomUserManager."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='pw')
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='super@user.com', password='pw', is_staff=False)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='super2@user.com', password='pw', is_superuser=False)

    def test_registration_failure_scenarios(self):
        """Test various failure scenarios for the registration API."""
        # Note: The user mentioned they removed the '/api' prefix, so I'll adjust the test URL.
        url = '/auth/registration/'

        # Scenario: Mismatched passwords
        mismatched_password_data = {
            "email": "a@b.com",
            "password1": "longpassword123",
            "password2": "longpassword456"  # These passwords are valid but don't match
        }
        response = self.client.post(url, mismatched_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('non_field_errors', response.data, "Error for mismatched passwords should be a non_field_error.")

        # Scenario: Email already exists
        existing_email_data = {
            "email": self.user_data['email'],
            "password1": "longpassword123",
            "password2": "longpassword123"
        }
        response = self.client.post(url, existing_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_failure_scenarios(self):
        """Test various failure scenarios for the login API."""
        url = '/auth/login/'
        response = self.client.post(url, {'email': self.user_data['email'], 'password': 'wrong-password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, {'email': 'nosuchuser@example.com', 'password': 'pw'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_details_update(self):
        """Test updating user details via PUT and PATCH."""
        self.client.force_authenticate(user=self.user)
        url = '/auth/user/'

        # Test PATCH (partial update)
        patch_data = {'first_name': 'UpdatedFirstName'}
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirstName')

        # Test PUT (full update)
        put_data = {'first_name': 'FinalFirstName', 'last_name': 'FinalLastName'}
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'FinalFirstName')
        self.assertEqual(self.user.last_name, 'FinalLastName')

        # Test trying to update read-only field (email)
        response = self.client.patch(url, {'email': 'cannot-change@me.com'}, format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.user_data['email'])  # Email should not change

    # --- Password Management Flow ---

    def test_password_change(self):
        """Test the password change flow for an authenticated user."""
        self.client.force_authenticate(user=self.user)
        url = '/auth/password/change/'
        data = {
            'old_password': self.user_data['password'],
            'new_password1': 'a-new-secure-password-456',
            'new_password2': 'a-new-secure-password-456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the new password works for login
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data['new_password1']))

    def test_password_reset_flow(self):
        """Test the full password reset flow from request to confirmation."""
        # --- Step 1: Request a password reset ---
        reset_url = '/auth/password/reset/'
        response = self.client.post(reset_url, {'email': self.user_data['email']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # Extract uid and token from the email body (this is robust)
        import re
        match = re.search(r'uid=([^&]+)&token=([^\s]+)', email_body)
        self.assertIsNotNone(match, "Could not find uid and token in the email.")
        uid = match.group(1)
        token = match.group(2)

        # --- Step 2: Confirm the password reset with the extracted data ---
        confirm_url = '/auth/password/reset/confirm/'
        new_password = 'reset-successfully-789'
        data = {
            'uid': uid,
            'token': token,
            'new_password1': new_password,
            'new_password2': new_password,
        }
        response = self.client.post(confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)

        # Verify the new password is set
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirmation with an invalid token."""
        url = '/auth/password/reset/confirm/'
        data = {'uid': 'invalid', 'token': 'invalid', 'new_password1': 'pw', 'new_password2': 'pw'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
