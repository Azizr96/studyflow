"""Handle study management, access permissions, and document uploads."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification
from notifications.utils import notify_study_users

from .forms import StudyDocumentForm, StudyForm
from .models import Study


def can_manage_studies(user):
    """Check whether a user has permission to manage studies."""

    # Users must be authenticated and have a profile with an assigned role.
    if not user.is_authenticated:
        return False

    if not hasattr(user, "profile"):
        return False

    if not user.profile.role:
        return False

    return user.profile.role.can_manage_studies


def can_access_study(user, study):
    """Check whether a user has permission to access a specific study."""

    # Users must be authenticated and have a profile with an assigned role.
    if not user.is_authenticated:
        return False

    if not hasattr(user, "profile"):
        return False

    if not user.profile.role:
        return False

    # Study managers are allowed to access all studies.
    if user.profile.role.can_manage_studies:
        return True

    # Standard users can only access studies actively assigned to them.
    return study.user_assignments.filter(
        user=user,
        is_active=True,
    ).exists()


@login_required
def create_study(request):
    """Create a new study when the user has study management permission."""

    # Only users with study management permission can create studies.
    if not can_manage_studies(request.user):
        messages.error(
            request,
            "You do not have permission to create studies.",
        )
        return redirect("accounts:login")

    if request.method == "POST":
        form = StudyForm(request.POST)

        if form.is_valid():
            study = form.save()

            messages.success(
                request,
                (
                    f"Study {study.protocol_number} "
                    "has been created successfully."
                ),
            )

            return redirect("studies:create_study")

    else:
        form = StudyForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "studies/create_study.html",
        context,
    )


@login_required
def study_list(request):
    """Display studies based on the user's role and assignments."""

    if not hasattr(request.user, "profile"):
        messages.error(
            request,
            "Your account profile could not be found.",
        )
        return redirect("accounts:login")

    if not request.user.profile.role:
        messages.error(
            request,
            "Your account does not have a role assigned.",
        )
        return redirect("accounts:login")

    # Study managers can view all studies in the system.
    if request.user.profile.role.can_manage_studies:
        studies = Study.objects.all().order_by(
            "protocol_number"
        )
    else:
        # Standard users only see studies actively assigned to them.
        studies = Study.objects.filter(
            user_assignments__user=request.user,
            user_assignments__is_active=True,
        ).order_by(
            "protocol_number"
        )

    context = {
        "studies": studies,
    }

    return render(
        request,
        "studies/study_list.html",
        context,
    )


@login_required
def study_detail(request, study_id):
    """Display a study and allow authorised users to upload documents."""

    study = get_object_or_404(
        Study,
        id=study_id,
    )

    # Prevent users from viewing studies they are not allowed to access.
    if not can_access_study(request.user, study):
        messages.error(
            request,
            "You do not have permission to access this study.",
        )
        return redirect("studies:study_list")

    if request.method == "POST":
        form = StudyDocumentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            # Add the study and uploader before saving because these
            # fields are not entered by the user through the form.
            document = form.save(commit=False)
            document.study = study
            document.uploaded_by = request.user
            document.save()

            # Notify other eligible users assigned to the same study.
            notify_study_users(
                study=study,
                title="Study Document Uploaded",
                message=(
                    f"A new {document.category} document "
                    f"has been uploaded to {study.protocol_number}."
                ),
                notification_type=Notification.Type.DOCUMENT_UPLOADED,
                exclude_user=request.user,
            )
            messages.success(
                request,
                "Study document uploaded successfully.",
            )

            return redirect(
                "studies:study_detail",
                study_id=study.id,
            )

    else:
        form = StudyDocumentForm()

    # Load the newest study documents first with their uploader details.
    documents = study.documents.select_related(
        "uploaded_by"
    ).order_by(
        "-uploaded_at"
    )

    # Keep participants ordered consistently by participant number.
    participants = study.participants.all().order_by(
        "participant_number"
    )

    context = {
        "study": study,
        "documents": documents,
        "participants": participants,
        "form": form,
    }

    return render(
        request,
        "studies/study_detail.html",
        context,
    )
