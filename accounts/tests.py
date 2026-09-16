from django.contrib.auth.models import User
from django.test import TestCase

from .forms import RegistrationForm
from .models import UserProfile, Role
from django.urls import reverse


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


class UserProfileSignalTests(TestCase):
    """Tests for automatic user profile creation."""

    def test_profile_created_for_new_user(self):
        """Creating a user should automatically create a profile."""
        user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="StrongTestPassword123!",
        )

        self.assertTrue(
            UserProfile.objects.filter(user=user).exists()
        )

    def test_new_user_is_not_approved(self):
        """A newly created user's profile should be unapproved."""
        user = User.objects.create_user(
            username="pendinguser",
            email="pending@example.com",
            password="StrongTestPassword123!",
        )

        profile = UserProfile.objects.get(user=user)

        self.assertFalse(profile.is_approved)


class LoginTests(TestCase):
    """Tests for StudyFlow login restrictions."""

    def test_unapproved_user_cannot_log_in(self):
        """An unapproved user should not be allowed to log in."""
        user = User.objects.create_user(
            username="pendinguser",
            email="pending@example.com",
            password="StrongTestPassword123!",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "pendinguser",
                "password": "StrongTestPassword123!",
            },
            follow=True,
        )

        self.assertFalse(user.profile.is_approved)
        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )
        self.assertContains(
            response,
            "Your account is awaiting approval.",
        )

    def test_approved_user_with_role_can_log_in(self):
        """An approved user with a role should be able to log in."""
        role = Role.objects.create(
            name="Study Coordinator",
            description="Standard study team member",
        )

        user = User.objects.create_user(
            username="approveduser",
            first_name="Approved",
            email="approved@example.com",
            password="StrongTestPassword123!",
        )

        user.profile.role = role
        user.profile.is_approved = True
        user.profile.save()

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "approveduser",
                "password": "StrongTestPassword123!",
            },
        )

        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )
        self.assertRedirects(
            response,
            reverse("dashboard:home"),
            fetch_redirect_response=False,
        )

    def test_approved_user_without_role_cannot_log_in(self):
        """An approved user without a role should not be allowed to log in."""
        user = User.objects.create_user(
            username="noroleuser",
            email="norole@example.com",
            password="StrongTestPassword123!",
        )

        user.profile.is_approved = True
        user.profile.save()

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "noroleuser",
                "password": "StrongTestPassword123!",
            },
            follow=True,
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )
        self.assertContains(
            response,
            "Your account does not have an assigned role.",
        )


class UserManagementPermissionTests(TestCase):
    """Tests for role-based access to user management."""

    def test_standard_user_cannot_access_user_list(self):
        """A standard user should not access user management."""
        role = Role.objects.create(
            name="Study Coordinator",
            can_manage_users=False,
        )

        user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="StrongTestPassword123!",
        )

        user.profile.role = role
        user.profile.is_approved = True
        user.profile.save()

        self.client.force_login(user)

        response = self.client.get(
            reverse("accounts:user_list")
        )

        self.assertRedirects(
            response,
            reverse("accounts:login"),
            fetch_redirect_response=False,
        )

    def test_manager_can_access_user_list(self):
        """A user manager should be able to access user management."""
        role = Role.objects.create(
            name="Project Lead",
            can_manage_users=True,
        )

        user = User.objects.create_user(
            username="projectlead",
            email="projectlead@example.com",
            password="StrongTestPassword123!",
        )

        user.profile.role = role
        user.profile.is_approved = True
        user.profile.save()

        self.client.force_login(user)

        response = self.client.get(
            reverse("accounts:user_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/user_list.html",
        )
