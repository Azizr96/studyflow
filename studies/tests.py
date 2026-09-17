from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, UserStudy

from .forms import StudyForm
from .models import Study

class StudyFormTests(TestCase):
    """Tests for StudyFlow study form validation."""

    def test_end_date_before_start_date_is_rejected(self):
        """A study end date cannot be before its start date."""
        form = StudyForm(
            data={
                "protocol_number": "SF-001",
                "title": "Test Clinical Study",
                "description": "Test study description.",
                "phase": "Phase 2",
                "status": "Planning",
                "start_date": "2026-09-10",
                "end_date": "2026-09-01",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "The end date cannot be before the start date.",
            form.non_field_errors(),
        )

    def test_valid_study_dates_are_accepted(self):
        """A study end date after its start date should be valid."""
        form = StudyForm(
            data={
                "protocol_number": "SF-002",
                "title": "Valid Clinical Study",
                "description": "Test study description.",
                "phase": "Phase 2",
                "status": "Planning",
                "start_date": "2026-09-01",
                "end_date": "2026-09-30",
            }
        )

        self.assertTrue(form.is_valid())


class StudyPermissionTests(TestCase):
    """Tests for role-based study permissions."""

    def test_standard_user_cannot_access_create_study(self):
        """A standard user should not access study creation."""
        role = Role.objects.create(
            name="Study Coordinator",
            can_manage_studies=False,
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
            reverse("studies:create_study")
        )

        self.assertRedirects(
            response,
            reverse("accounts:login"),
            fetch_redirect_response=False,
        )

    def test_manager_can_access_create_study(self):
        """A study manager should be able to access study creation."""
        role = Role.objects.create(
            name="Project Lead",
            can_manage_studies=True,
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
            reverse("studies:create_study")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "studies/create_study.html",
        )


class StudyListTests(TestCase):
    """Tests for role-based study list visibility."""

    def test_standard_user_sees_only_assigned_studies(self):
        """A standard user should only see actively assigned studies."""
        role = Role.objects.create(
            name="Study Coordinator",
            can_manage_studies=False,
        )

        user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="StrongTestPassword123!",
        )

        user.profile.role = role
        user.profile.is_approved = True
        user.profile.save()

        assigned_study = Study.objects.create(
            protocol_number="SF-101",
            title="Assigned Study",
            phase="Phase 2",
            status="Active",
        )

        unassigned_study = Study.objects.create(
            protocol_number="SF-102",
            title="Unassigned Study",
            phase="Phase 3",
            status="Recruiting",
        )

        UserStudy.objects.create(
            user=user,
            study=assigned_study,
            is_active=True,
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("studies:study_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Assigned Study",
        )
        self.assertNotContains(
            response,
            "Unassigned Study",
        )