from accounts.models import UserStudy
from .models import Notification


def create_notification(
    user,
    title,
    message,
    notification_type,
):
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
    assignments = UserStudy.objects.filter(
        study=study,
        is_active=True,
        user__is_active=True,
        user__profile__is_approved=True,
    ).select_related("user")

    for assignment in assignments:
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
