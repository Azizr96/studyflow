from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, UserStudy
from studies.models import Study

from .forms import ParticipantForm, VisitForm
from .models import Participant, Visit


class ParticipantFormTests(TestCase):
    """Tests for participant form validation."""

    def test_enrolled_date_before_date_of_birth_is_rejected(self):
        """Enrolment cannot take place before date of birth."""
        form = ParticipantForm(
            data={
                "participant_number": "p-001",
                "first_name": "Test",
                "last_name": "Participant",
                "date_of_birth": "1990-01-01",
                "sex": "Male",
                "status": "Enrolled",
                "enrolled_date": "1989-12-31",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "The enrolled date must be after "
            "the participant's date of birth.",
            form.non_field_errors(),
        )

    def test_valid_participant_data_is_accepted(self):
        """Valid participant data should pass validation."""
        form = ParticipantForm(
            data={
                "participant_number": "P-002",
                "first_name": "Test",
                "last_name": "Participant",
                "date_of_birth": "1990-01-01",
                "sex": "Female",
                "status": "Enrolled",
                "enrolled_date": "2026-01-10",
            }
        )

        self.assertTrue(form.is_valid())

    def test_participant_number_is_converted_to_uppercase(self):
        """Participant numbers should be normalised to uppercase."""
        form = ParticipantForm(
            data={
                "participant_number": "sf-003",
                "first_name": "Test",
                "last_name": "Participant",
                "date_of_birth": "1990-01-01",
                "sex": "Male",
                "status": "Active",
                "enrolled_date": "2026-01-10",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["participant_number"],
            "SF-003",
        )


class VisitFormTests(TestCase):
    """Tests for visit form validation."""

    def setUp(self):
        self.study = Study.objects.create(
            protocol_number="VIS-001",
            title="Visit Test Study",
            phase="Phase 2",
            status="Active",
        )

        self.participant = Participant.objects.create(
            study=self.study,
            participant_number="VIS-P001",
            first_name="Test",
            last_name="Participant",
            date_of_birth=date(1990, 1, 1),
            sex="Male",
            status="Active",
            enrolled_date=date(2026, 1, 1),
        )

    def test_duplicate_visit_number_is_rejected(self):
        """A participant cannot have the same visit number twice."""
        Visit.objects.create(
            participant=self.participant,
            visit_number=1,
            visit_type="Baseline",
            scheduled_date=date(2026, 9, 20),
            status="Scheduled",
        )

        form = VisitForm(
            data={
                "visit_number": 1,
                "visit_type": "Follow Up",
                "scheduled_date": "2026-10-01",
                "actual_date": "",
                "status": "Scheduled",
                "notes": "",
            },
            participant=self.participant,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("visit_number", form.errors)

    def test_actual_date_before_scheduled_date_is_rejected(self):
        """Actual visit date cannot precede the scheduled date."""
        form = VisitForm(
            data={
                "visit_number": 2,
                "visit_type": "Follow Up",
                "scheduled_date": "2026-09-20",
                "actual_date": "2026-09-19",
                "status": "Completed",
                "notes": "",
            },
            participant=self.participant,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "The actual visit date cannot be before "
            "the scheduled date.",
            form.non_field_errors(),
        )

    def test_completed_visit_without_actual_date_is_rejected(self):
        """A completed visit must include an actual visit date."""
        form = VisitForm(
            data={
                "visit_number": 3,
                "visit_type": "Follow Up",
                "scheduled_date": "2026-09-20",
                "actual_date": "",
                "status": "Completed",
                "notes": "",
            },
            participant=self.participant,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "A completed visit must have an actual visit date.",
            form.non_field_errors(),
        )

    def test_valid_visit_data_is_accepted(self):
        """Valid visit data should pass validation."""
        form = VisitForm(
            data={
                "visit_number": 4,
                "visit_type": "Follow Up",
                "scheduled_date": "2026-09-20",
                "actual_date": "2026-09-20",
                "status": "Completed",
                "notes": "Visit completed successfully.",
            },
            participant=self.participant,
        )

        self.assertTrue(form.is_valid())


class ParticipantPermissionTests(TestCase):
    """Tests for participant access permissions."""

    def setUp(self):
        self.role = Role.objects.create(
            name="Study Coordinator",
            can_manage_studies=False,
        )

        self.user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="StrongTestPassword123!",
        )

        self.user.profile.role = self.role
        self.user.profile.is_approved = True
        self.user.profile.save()

        self.assigned_study = Study.objects.create(
            protocol_number="PERM-001",
            title="Assigned Study",
            phase="Phase 2",
            status="Active",
        )

        self.unassigned_study = Study.objects.create(
            protocol_number="PERM-002",
            title="Unassigned Study",
            phase="Phase 3",
            status="Active",
        )

        UserStudy.objects.create(
            user=self.user,
            study=self.assigned_study,
            is_active=True,
        )

        self.protected_participant = Participant.objects.create(
            study=self.unassigned_study,
            participant_number="PROTECTED-001",
            first_name="Protected",
            last_name="Participant",
            date_of_birth=date(1990, 1, 1),
            sex="Female",
            status="Active",
            enrolled_date=date(2026, 1, 1),
        )

        self.client.force_login(self.user)

    def test_user_cannot_update_participant_in_unassigned_study(self):
        """A user cannot update a participant outside their studies."""
        response = self.client.get(
            reverse(
                "participants:update_participant",
                args=[self.protected_participant.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("participants:participant_list"),
            fetch_redirect_response=False,
        )

    def test_user_cannot_delete_participant_in_unassigned_study(self):
        """A user cannot delete a participant outside their studies."""
        response = self.client.post(
            reverse(
                "participants:delete_participant",
                args=[self.protected_participant.id],
            ),
            {
                "confirm_delete": "DELETE",
                "password": "StrongTestPassword123!",
            },
        )

        self.assertTrue(
            Participant.objects.filter(
                id=self.protected_participant.id
            ).exists()
        )

        self.assertRedirects(
            response,
            reverse("participants:participant_list"),
            fetch_redirect_response=False,
        )


class VisitPermissionTests(TestCase):
    """Tests for visit access permissions."""

    def setUp(self):
        self.role = Role.objects.create(
            name="Study Coordinator",
            can_manage_studies=False,
        )

        self.user = User.objects.create_user(
            username="visitcoordinator",
            email="visitcoordinator@example.com",
            password="StrongTestPassword123!",
        )

        self.user.profile.role = self.role
        self.user.profile.is_approved = True
        self.user.profile.save()

        self.assigned_study = Study.objects.create(
            protocol_number="VIS-PERM-001",
            title="Assigned Visit Study",
            phase="Phase 2",
            status="Active",
        )

        self.unassigned_study = Study.objects.create(
            protocol_number="VIS-PERM-002",
            title="Protected Visit Study",
            phase="Phase 3",
            status="Active",
        )

        UserStudy.objects.create(
            user=self.user,
            study=self.assigned_study,
            is_active=True,
        )

        self.participant = Participant.objects.create(
            study=self.unassigned_study,
            participant_number="VIS-PROTECTED",
            first_name="Protected",
            last_name="Participant",
            date_of_birth=date(1990, 1, 1),
            sex="Male",
            status="Active",
            enrolled_date=date(2026, 1, 1),
        )

        self.visit = Visit.objects.create(
            participant=self.participant,
            visit_number=1,
            visit_type="Baseline",
            scheduled_date=date(2026, 9, 20),
            status="Scheduled",
        )

        self.client.force_login(self.user)

    def test_user_cannot_update_visit_in_unassigned_study(self):
        """A user cannot update a visit outside their studies."""
        response = self.client.get(
            reverse(
                "participants:update_visit",
                args=[self.visit.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("participants:visit_list"),
            fetch_redirect_response=False,
        )

    def test_user_cannot_delete_visit_in_unassigned_study(self):
        """A user cannot delete a visit outside their studies."""
        response = self.client.post(
            reverse(
                "participants:delete_visit",
                args=[self.visit.id],
            ),
            {
                "confirm_delete": "DELETE",
                "password": "StrongTestPassword123!",
            },
        )

        self.assertTrue(
            Visit.objects.filter(
                id=self.visit.id
            ).exists()
        )

        self.assertRedirects(
            response,
            reverse("participants:visit_list"),
            fetch_redirect_response=False,
        )
