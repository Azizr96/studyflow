from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, UserStudy

from .forms import StudyForm, StudyDocumentForm
from .models import Study
from django.core.files.uploadedfile import SimpleUploadedFile


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

    def test_standard_user_does_not_see_inactive_assignment(self):
        """A standard user should not see an inactive study assignment."""
        role = Role.objects.create(
            name="Study Coordinator",
            can_manage_studies=False,
        )

        user = User.objects.create_user(
            username="inactivecoordinator",
            email="inactive@example.com",
            password="StrongTestPassword123!",
        )

        user.profile.role = role
        user.profile.is_approved = True
        user.profile.save()

        study = Study.objects.create(
            protocol_number="SF-103",
            title="Inactive Assignment Study",
            phase="Phase 2",
            status="Active",
        )

        UserStudy.objects.create(
            user=user,
            study=study,
            is_active=False,
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("studies:study_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Inactive Assignment Study",
        )

    def test_manager_sees_all_studies(self):
        """A study manager should see all studies."""
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

        Study.objects.create(
            protocol_number="SF-201",
            title="First Global Study",
            phase="Phase 2",
            status="Active",
        )

        Study.objects.create(
            protocol_number="SF-202",
            title="Second Global Study",
            phase="Phase 3",
            status="Recruiting",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("studies:study_list")
        )

        self.assertContains(response, "First Global Study")
        self.assertContains(response, "Second Global Study")


class StudyDetailPermissionTests(TestCase):
    """Tests for access to individual study pages."""

    def test_standard_user_cannot_access_unassigned_study(self):
        """A standard user should not access an unassigned study."""
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
            protocol_number="SF-301",
            title="Assigned Study",
            phase="Phase 2",
            status="Active",
        )

        unassigned_study = Study.objects.create(
            protocol_number="SF-302",
            title="Protected Study",
            phase="Phase 3",
            status="Active",
        )

        UserStudy.objects.create(
            user=user,
            study=assigned_study,
            is_active=True,
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse(
                "studies:study_detail",
                args=[unassigned_study.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("studies:study_list"),
            fetch_redirect_response=False,
        )


class StudyDocumentFormTests(TestCase):
    """Tests for study document validation."""

    def test_invalid_document_extension_is_rejected(self):
        """Unsupported study document file types should be rejected."""
        uploaded_file = SimpleUploadedFile(
            "malicious.exe",
            b"test file content",
            content_type="application/octet-stream",
        )

        form = StudyDocumentForm(
            data={
                "category": "Protocol",
                "version": "1.0",
            },
            files={
                "file": uploaded_file,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)

    def test_document_larger_than_ten_mb_is_rejected(self):
        """Study documents larger than 10 MB should be rejected."""
        uploaded_file = SimpleUploadedFile(
            "large-document.pdf",
            b"x" * (10 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )

        form = StudyDocumentForm(
            data={
                "category": "Protocol",
                "version": "1.0",
            },
            files={
                "file": uploaded_file,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)
