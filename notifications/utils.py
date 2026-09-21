"""Provide helper functions for creating StudyFlow notifications."""

from accounts.models import UserStudy
from .models import Notification


def create_notification(
    user,
    title,
    message,
    notification_type,
):
    """Create a notification for a specific user."""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type,
    )


def notify_study_users(
    study,
    title,
    message,
    notification_type,
    exclude_user=None,
):
    """Create notifications for eligible users assigned to a study."""

    # Only notify users with an active study assignment who also
    # have an active and approved StudyFlow account.
    assignments = UserStudy.objects.filter(
        study=study,
        is_active=True,
        user__is_active=True,
        user__profile__is_approved=True,
    ).select_related("user")

    for assignment in assignments:
        # Skip the excluded user, such as the person who triggered
        # the action that created the notification.
        if (
            exclude_user
            and assignment.user_id == exclude_user.id
        ):
            continue

        Notification.objects.create(
            user=assignment.user,
            title=title,
            message=message,
            type=notification_type,
        )
