from django.contrib.auth.models import User
from django.test import TestCase

from .forms import RegistrationForm


class RegistrationFormTests(TestCase):
    """Tests for the StudyFlow user registration form."""

    def test_valid_registration_form(self):
        """A form with valid registration data should be valid."""
        form = RegistrationForm(
            data={
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "password1": "StrongTestPassword123!",
                "password2": "StrongTestPassword123!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_duplicate_email_is_rejected(self):
        """An email already used by another user should be rejected."""
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="StrongTestPassword123!",
        )

        form = RegistrationForm(
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "existing@example.com",
                "password1": "StrongTestPassword123!",
                "password2": "StrongTestPassword123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn(
            "An account with this email already exists.",
            form.errors["email"],
        )

    def test_password_mismatch_is_rejected(self):
        """Different password entries should make the form invalid."""
        form = RegistrationForm(
            data={
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "password1": "StrongTestPassword123!",
                "password2": "DifferentTestPassword123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
