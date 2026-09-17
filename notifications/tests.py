from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, UserStudy
from studies.models import Study

from .models import Notification
from .utils import notify_study_users


class NotificationViewTests(TestCase):
    """Tests for notification access and ownership."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="notificationuser",
            email="notification@example.com",
            password="StrongTestPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongTestPassword123!",
        )

        self.own_notification = Notification.objects.create(
            user=self.user,
            title="My Notification",
            message="This notification belongs to the logged-in user.",
            type=Notification.Type.GENERAL,
        )

        self.other_notification = Notification.objects.create(
            user=self.other_user,
            title="Other User Notification",
            message="This belongs to another user.",
            type=Notification.Type.GENERAL,
        )

        self.client.force_login(self.user)

    def test_user_sees_own_notification(self):
        """A user should see notifications belonging to them."""
        response = self.client.get(
            reverse("notifications:notification_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "My Notification",
        )

    def test_user_does_not_see_another_users_notification(self):
        """A user should not see another user's notifications."""
        response = self.client.get(
            reverse("notifications:notification_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Other User Notification",
        )

    def test_user_can_mark_own_notification_as_read(self):
        """A user should be able to mark their notification as read."""
        response = self.client.post(
            reverse(
                "notifications:mark_notification_read",
                args=[self.own_notification.id],
            )
        )

        self.own_notification.refresh_from_db()

        self.assertTrue(self.own_notification.is_read)

        self.assertRedirects(
            response,
            reverse("notifications:notification_list"),
            fetch_redirect_response=False,
        )

    def test_user_cannot_mark_another_users_notification_as_read(self):
        """
        A user should not be able to mark
        another user's notification as read.
        """
        response = self.client.post(
            reverse(
                "notifications:mark_notification_read",
                args=[self.other_notification.id],
            )
        )

        self.other_notification.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.other_notification.is_read)

    def test_mark_all_only_updates_logged_in_user_notifications(self):
        """Mark all should not modify another user's notifications."""
        response = self.client.post(
            reverse("notifications:mark_all_notifications_read")
        )

        self.own_notification.refresh_from_db()
        self.other_notification.refresh_from_db()

        self.assertTrue(self.own_notification.is_read)
        self.assertFalse(self.other_notification.is_read)

        self.assertRedirects(
            response,
            reverse("notifications:notification_list"),
            fetch_redirect_response=False,
        )


class NotificationUtilityTests(TestCase):
    """Tests for study notification creation."""

    def test_notify_study_users_only_notifies_eligible_users(self):
        """Only eligible assigned users should receive notifications."""
        role = Role.objects.create(
            name="Study Coordinator",
            can_manage_studies=False,
        )

        study = Study.objects.create(
            protocol_number="NOT-001",
            title="Notification Test Study",
            phase="Phase 2",
            status="Active",
        )

        actor = User.objects.create_user(
            username="actor",
            email="actor@example.com",
            password="StrongTestPassword123!",
        )

        recipient = User.objects.create_user(
            username="recipient",
            email="recipient@example.com",
            password="StrongTestPassword123!",
        )

        unassigned_user = User.objects.create_user(
            username="unassigned",
            email="unassigned@example.com",
            password="StrongTestPassword123!",
        )

        for user in [actor, recipient, unassigned_user]:
            user.profile.role = role
            user.profile.is_approved = True
            user.profile.save()

        UserStudy.objects.create(
            user=actor,
            study=study,
            is_active=True,
        )

        UserStudy.objects.create(
            user=recipient,
            study=study,
            is_active=True,
        )

        notify_study_users(
            study=study,
            title="Participant Added",
            message="A participant was added.",
            notification_type=Notification.Type.PARTICIPANT_ADDED,
            exclude_user=actor,
        )

        self.assertFalse(
            Notification.objects.filter(
                user=actor,
                title="Participant Added",
            ).exists()
        )

        self.assertTrue(
            Notification.objects.filter(
                user=recipient,
                title="Participant Added",
            ).exists()
        )

        self.assertFalse(
            Notification.objects.filter(
                user=unassigned_user,
                title="Participant Added",
            ).exists()
        )
