from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from accounts.models import UserProfile
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

    is_elevated = (
        role.is_admin
        or role.can_manage_users
        or role.can_manage_studies
    )

    if not is_elevated:
        return redirect("studies:study_list")

    today = timezone.localdate()

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

    context = {
        "total_studies": total_studies,
        "total_participants": total_participants,
        "total_visits": total_visits,
        "pending_users": pending_users,
        "upcoming_visits": upcoming_visits,
        "recent_documents": recent_documents,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )