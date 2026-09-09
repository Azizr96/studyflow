from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from studies.models import Study
from .forms import ParticipantForm


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
def add_participant(request, study_id):
    study = get_object_or_404(
        Study,
        id=study_id,
    )

    if not can_access_study(request.user, study):
        messages.error(
            request,
            "You do not have permission to add "
            "participants to this study.",
        )
        return redirect("studies:study_list")

    if request.method == "POST":
        form = ParticipantForm(request.POST)

        if form.is_valid():
            participant = form.save(commit=False)
            participant.study = study
            participant.save()

            messages.success(
                request,
                (
                    f"Participant "
                    f"{participant.participant_number} "
                    "has been added successfully."
                ),
            )

            return redirect(
                "studies:study_detail",
                study_id=study.id,
            )

    else:
        form = ParticipantForm()

    context = {
        "form": form,
        "study": study,
    }

    return render(
        request,
        "participants/add_participant.html",
        context,
    )