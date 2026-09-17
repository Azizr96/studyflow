from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role, UserStudy
from participants.models import Participant, Visit
from studies.models import Study


class DashboardTests(TestCase):
    """Tests for role-based dashboard data."""

    def setUp(self):
        self.standard_role = Role.objects.create(
            name="Study Coordinator",
            can_manage_studies=False,
            can_manage_users=False,
            is_admin=False,
        )

        self.elevated_role = Role.objects.create(
            name="Project Lead",
            can_manage_studies=True,
            can_manage_users=True,
        )

        self.assigned_study = Study.objects.create(
            protocol_number="DASH-001",
            title="Assigned Dashboard Study",
            phase="Phase 2",
            status="Active",
        )

        self.unassigned_study = Study.objects.create(
            protocol_number="DASH-002",
            title="Unassigned Dashboard Study",
            phase="Phase 3",
            status="Active",
        )

        self.assigned_participant = Participant.objects.create(
            study=self.assigned_study,
            participant_number="DASH-P001",
            first_name="Assigned",
            last_name="Participant",
            date_of_birth=date(1990, 1, 1),
            sex="Male",
            status="Active",
            enrolled_date=date(2026, 1, 1),
        )

        self.unassigned_participant = Participant.objects.create(
            study=self.unassigned_study,
            participant_number="DASH-P002",
            first_name="Unassigned",
            last_name="Participant",
            date_of_birth=date(1990, 1, 1),
            sex="Female",
            status="Active",
            enrolled_date=date(2026, 1, 1),
        )

        tomorrow = timezone.localdate() + timedelta(days=1)

        Visit.objects.create(
            participant=self.assigned_participant,
            visit_number=1,
            visit_type="Baseline",
            scheduled_date=tomorrow,
            status="Scheduled",
        )

        Visit.objects.create(
            participant=self.unassigned_participant,
            visit_number=1,
            visit_type="Baseline",
            scheduled_date=tomorrow,
            status="Scheduled",
        )

    def test_standard_user_dashboard_only_counts_assigned_study_data(self):
        """Standard dashboard data should be limited to assigned studies."""
        user = User.objects.create_user(
            username="dashboardcoordinator",
            email="dashboardcoordinator@example.com",
            password="StrongTestPassword123!",
        )

        user.profile.role = self.standard_role
        user.profile.is_approved = True
        user.profile.save()

        UserStudy.objects.create(
            user=user,
            study=self.assigned_study,
            is_active=True,
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("dashboard:home")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["dashboard_type"],
            "standard",
        )
        self.assertEqual(
            response.context["total_studies"],
            1,
        )
        self.assertEqual(
            response.context["total_participants"],
            1,
        )
        self.assertEqual(
            response.context["total_visits"],
            1,
        )
        self.assertEqual(
            len(response.context["upcoming_visits"]),
            1,
        )

    def test_elevated_user_dashboard_counts_global_data(self):
        """Elevated dashboard statistics should include all studies."""
        user = User.objects.create_user(
            username="projectlead",
            email="projectlead@example.com",
            password="StrongTestPassword123!",
        )

        user.profile.role = self.elevated_role
        user.profile.is_approved = True
        user.profile.save()

        self.client.force_login(user)

        response = self.client.get(
            reverse("dashboard:home")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["dashboard_type"],
            "elevated",
        )
        self.assertEqual(
            response.context["total_studies"],
            2,
        )
        self.assertEqual(
            response.context["total_participants"],
            2,
        )
        self.assertEqual(
            response.context["total_visits"],
            2,
        )
        self.assertEqual(
            len(response.context["upcoming_visits"]),
            2,
        )
