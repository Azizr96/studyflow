from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.models import UserProfile
from notifications.models import Notification
from participants.models import Participant, Visit
from studies.models import Study, StudyDocument


@login_required
def dashboard_home(request):
    try:
        role = request.user.profile.role
    except AttributeError:
        role = None

    if not role:
        return redirect("accounts:login")

    today = timezone.localdate()

    recent_notifications = Notification.objects.filter(
        user=request.user,
    ).order_by("-created_at")[:5]

    unread_notification_count = Notification.objects.filter(
        user=request.user,
        is_read=False,
    ).count()

    is_elevated = (
        role.is_admin
        or role.can_manage_users
        or role.can_manage_studies
    )

    if is_elevated:
        total_studies = Study.objects.count()
        total_participants = Participant.objects.count()
        total_visits = Visit.objects.count()

        pending_users = UserProfile.objects.filter(
            is_approved=False,
        ).count()

        upcoming_visits = Visit.objects.select_related(
            "participant",
            "participant__study",
        ).filter(
            scheduled_date__gte=today,
            status=Visit.Status.SCHEDULED,
        ).order_by(
            "scheduled_date",
        )[:5]

        recent_documents = StudyDocument.objects.select_related(
            "study",
            "uploaded_by",
        ).order_by(
            "-uploaded_at",
        )[:5]

        dashboard_type = "elevated"

    else:
        assigned_studies = Study.objects.filter(
            user_assignments__user=request.user,
            user_assignments__is_active=True,
        ).distinct()

        total_studies = assigned_studies.count()

        total_participants = Participant.objects.filter(
            study__in=assigned_studies,
        ).count()

        total_visits = Visit.objects.filter(
            participant__study__in=assigned_studies,
        ).count()

        pending_users = None

        upcoming_visits = Visit.objects.select_related(
            "participant",
            "participant__study",
        ).filter(
            participant__study__in=assigned_studies,
            scheduled_date__gte=today,
            status=Visit.Status.SCHEDULED,
        ).order_by(
            "scheduled_date",
        )[:5]

        recent_documents = StudyDocument.objects.select_related(
            "study",
            "uploaded_by",
        ).filter(
            study__in=assigned_studies,
        ).order_by(
            "-uploaded_at",
        )[:5]

        dashboard_type = "standard"

    context = {
        "dashboard_type": dashboard_type,
        "total_studies": total_studies,
        "total_participants": total_participants,
        "total_visits": total_visits,
        "pending_users": pending_users,
        "upcoming_visits": upcoming_visits,
        "recent_documents": recent_documents,
        "recent_notifications": recent_notifications,
        "unread_notification_count": unread_notification_count,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )
