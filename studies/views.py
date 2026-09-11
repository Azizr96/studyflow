from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from .forms import StudyForm, StudyDocumentForm
from .models import Study
from notifications.models import Notification
from notifications.utils import notify_study_users

def can_manage_studies(user):
    if not user.is_authenticated:
        return False

    if not hasattr(user, "profile"):
        return False

    if not user.profile.role:
        return False

    return user.profile.role.can_manage_studies

def can_access_study(user, study):
    if not user.is_authenticated:
        return False

    if not hasattr(user, "profile"):
        return False

    if not user.profile.role:
        return False

    if user.profile.role.can_manage_studies:
        return True

    return study.user_assignments.filter(
        user=user,
        is_active=True,
    ).exists()


@login_required
def create_study(request):
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

    if request.user.profile.role.can_manage_studies:
        studies = Study.objects.all().order_by(
            "protocol_number"
        )
    else:
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
    study = get_object_or_404(
        Study,
        id=study_id,
    )

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
            document = form.save(commit=False)
            document.study = study
            document.uploaded_by = request.user
            document.save()

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

    documents = study.documents.select_related(
        "uploaded_by"
    ).order_by(
        "-uploaded_at"
    )

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