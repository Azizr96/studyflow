"""Handle participant and visit management views and permissions."""

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification
from notifications.utils import notify_study_users
from studies.models import Study

from .forms import ParticipantForm, VisitForm
from .models import Participant, Visit


def can_access_study(user, study):
    """Check whether a user has permission to access a study."""

    # Users must be authenticated and have a profile with an assigned role.
    if not user.is_authenticated:
        return False

    if not hasattr(user, "profile"):
        return False

    if not user.profile.role:
        return False

    # Users who manage studies are allowed to access all studies.
    if user.profile.role.can_manage_studies:
        return True

    # Standard users can only access studies actively assigned to them.
    return study.user_assignments.filter(
        user=user,
        is_active=True,
    ).exists()


@login_required
def add_participant(request, study_id):
    """Add a participant to a study the user can access."""

    study = get_object_or_404(
        Study,
        id=study_id,
    )

    # Prevent users from adding participants to unauthorised studies.
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
            # Add the study before saving because it is not a form field.
            participant = form.save(commit=False)
            participant.study = study
            participant.save()

            # Notify other eligible users assigned to the same study.
            notify_study_users(
                study=study,
                title="Participant Added",
                message=(
                    f"Participant {participant.participant_number} "
                    f"has been added to {study.protocol_number}."
                ),
                notification_type=Notification.Type.PARTICIPANT_ADDED,
                exclude_user=request.user,
            )
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


@login_required
def participant_list(request):
    """Display participants based on the user's study access."""

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

    # Study managers can view participants across all studies.
    if request.user.profile.role.can_manage_studies:
        participants = Participant.objects.select_related(
            "study"
        ).all().order_by(
            "participant_number"
        )
    else:
        # Standard users only see participants from actively assigned studies.
        participants = Participant.objects.select_related(
            "study"
        ).filter(
            study__user_assignments__user=request.user,
            study__user_assignments__is_active=True,
        ).order_by(
            "participant_number"
        )

    context = {
        "participants": participants,
    }

    return render(
        request,
        "participants/participant_list.html",
        context,
    )


@login_required
def update_participant(request, participant_id):
    """Update a participant when the user can access their study."""

    participant = get_object_or_404(
        Participant.objects.select_related("study"),
        id=participant_id,
    )

    # Check study access before allowing participant changes.
    if not can_access_study(
        request.user,
        participant.study,
    ):
        messages.error(
            request,
            "You do not have permission to update this participant.",
        )
        return redirect(
            "participants:participant_list"
        )

    if request.method == "POST":
        form = ParticipantForm(
            request.POST,
            instance=participant,
        )

        if form.is_valid():
            participant = form.save()

            messages.success(
                request,
                (
                    f"Participant "
                    f"{participant.participant_number} "
                    "has been updated successfully."
                ),
            )

            return redirect(
                "studies:study_detail",
                study_id=participant.study.id,
            )

    else:
        form = ParticipantForm(
            instance=participant,
        )

    context = {
        "form": form,
        "participant": participant,
        "study": participant.study,
    }

    return render(
        request,
        "participants/update_participant.html",
        context,
    )


@login_required
def delete_participant(request, participant_id):
    """Delete a participant after confirmation and password verification."""

    participant = get_object_or_404(
        Participant.objects.select_related("study"),
        id=participant_id,
    )

    # Check study access before allowing participant deletion.
    if not can_access_study(
        request.user,
        participant.study,
    ):
        messages.error(
            request,
            "You do not have permission to delete this participant.",
        )
        return redirect(
            "participants:participant_list"
        )

    if request.method == "POST":
        confirmation = request.POST.get("confirm_delete")
        password = request.POST.get("password")

        # Require an exact confirmation before performing the deletion.
        if confirmation != "DELETE":
            messages.error(
                request,
                "Please type DELETE to confirm deletion.",
            )
            return redirect(
                "participants:delete_participant",
                participant_id=participant.id,
            )

        # Re-authenticate the current user as an extra deletion safeguard.
        authenticated_user = authenticate(
            request,
            username=request.user.username,
            password=password,
        )

        if authenticated_user is None:
            messages.error(
                request,
                "Your password was incorrect. Participant was not deleted.",
            )
            return redirect(
                "participants:delete_participant",
                participant_id=participant.id,
            )

        # Save these values because the participant is about to be deleted.
        participant_number = participant.participant_number
        study_id = participant.study.id

        participant.delete()

        messages.success(
            request,
            (
                f"Participant {participant_number} "
                "has been deleted successfully."
            ),
        )

        return redirect(
            "studies:study_detail",
            study_id=study_id,
        )

    context = {
        "participant": participant,
        "study": participant.study,
    }

    return render(
        request,
        "participants/delete_participant.html",
        context,
    )


@login_required
def add_visit(request, participant_id):
    """Add a visit for a participant the user can access."""

    participant = get_object_or_404(
        Participant.objects.select_related("study"),
        id=participant_id,
    )

    study = participant.study

    # Visit access is controlled through the participant's study.
    if not can_access_study(request.user, study):
        messages.error(
            request,
            "You do not have permission to add visits to this participant.",
        )
        return redirect("participants:participant_list")

    if request.method == "POST":
        form = VisitForm(
            request.POST,
            participant=participant,
        )

        if form.is_valid():
            # Add the participant before saving because it is not a form field.
            visit = form.save(commit=False)
            visit.participant = participant
            visit.save()

            # Notify other eligible study users about the scheduled visit.
            notify_study_users(
                study=study,
                title="Upcoming Visit",
                message=(
                    f"Visit {visit.visit_number} for participant "
                    f"{participant.participant_number} is scheduled for "
                    f"{visit.scheduled_date} in {study.protocol_number}."
                ),
                notification_type=Notification.Type.VISIT_REMINDER,
                exclude_user=request.user,
            )

            messages.success(
                request,
                f"Visit {visit.visit_number} was added successfully.",
            )

            return redirect(
                "studies:study_detail",
                study_id=study.id,
            )

    else:
        form = VisitForm(
            participant=participant,
        )

    return render(
        request,
        "participants/add_visit.html",
        {
            "form": form,
            "participant": participant,
            "study": study,
        },
    )


@login_required
def visit_list(request):
    """Display visits based on the user's role and study assignments."""

    # Safely retrieve the role in case the user's profile is missing.
    try:
        role = request.user.profile.role
    except AttributeError:
        role = None

    if not role:
        messages.error(
            request,
            "You do not have permission to view visits.",
        )
        return redirect("accounts:login")

    # Study managers can view visits across all studies.
    if role.can_manage_studies:
        visits = Visit.objects.select_related(
            "participant",
            "participant__study",
        ).all()
    else:
        # Standard users only see visits from actively assigned studies.
        visits = Visit.objects.select_related(
            "participant",
            "participant__study",
        ).filter(
            participant__study__user_assignments__user=request.user,
            participant__study__user_assignments__is_active=True,
        )

    visits = visits.order_by(
        "scheduled_date",
        "participant__participant_number",
    )

    return render(
        request,
        "participants/visit_list.html",
        {
            "visits": visits,
        },
    )


@login_required
def update_visit(request, visit_id):
    """Update a visit and notify users when it becomes completed."""

    visit = get_object_or_404(
        Visit.objects.select_related(
            "participant",
            "participant__study",
        ),
        id=visit_id,
    )

    participant = visit.participant
    study = participant.study

    # Store the current status before the form can change the visit.
    original_status = visit.status

    if not can_access_study(request.user, study):
        messages.error(
            request,
            "You do not have permission to update this visit.",
        )
        return redirect("participants:visit_list")

    if request.method == "POST":
        form = VisitForm(
            request.POST,
            instance=visit,
            participant=participant,
        )

        if form.is_valid():
            updated_visit = form.save()

            # Send a notification only when the visit changes from
            # another status to completed.
            if (
                original_status != Visit.Status.COMPLETED
                and updated_visit.status == Visit.Status.COMPLETED
            ):
                notify_study_users(
                    study=study,
                    title="Visit Completed",
                    message=(
                        f"Visit {updated_visit.visit_number} for participant "
                        f"{participant.participant_number} has been completed "
                        f"in {study.protocol_number}."
                    ),
                    notification_type=Notification.Type.VISIT_COMPLETED,
                    exclude_user=request.user,
                )

            messages.success(
                request,
                f"Visit {updated_visit.visit_number} was updated "
                "successfully.",
            )

            return redirect("participants:visit_list")

    else:
        form = VisitForm(
            instance=visit,
            participant=participant,
        )

    return render(
        request,
        "participants/update_visit.html",
        {
            "form": form,
            "visit": visit,
            "participant": participant,
            "study": study,
        },
    )


@login_required
def delete_visit(request, visit_id):
    """Delete a visit after confirmation and password verification."""

    visit = get_object_or_404(
        Visit.objects.select_related(
            "participant",
            "participant__study",
        ),
        id=visit_id,
    )

    participant = visit.participant
    study = participant.study

    # Check study access before allowing visit deletion.
    if not can_access_study(request.user, study):
        messages.error(
            request,
            "You do not have permission to delete this visit.",
        )
        return redirect("participants:visit_list")

    if request.method == "POST":
        confirm_delete = request.POST.get("confirm_delete", "").strip()
        password = request.POST.get("password", "")

        # Require an exact confirmation before performing the deletion.
        if confirm_delete != "DELETE":
            messages.error(
                request,
                "You must type DELETE exactly to confirm.",
            )
            return render(
                request,
                "participants/delete_visit.html",
                {
                    "visit": visit,
                    "participant": participant,
                    "study": study,
                },
            )

        # Re-authenticate the current user as an extra deletion safeguard.
        authenticated_user = authenticate(
            request,
            username=request.user.username,
            password=password,
        )

        if authenticated_user is None:
            messages.error(
                request,
                "Your password was incorrect.",
            )
            return render(
                request,
                "participants/delete_visit.html",
                {
                    "visit": visit,
                    "participant": participant,
                    "study": study,
                },
            )

        # Store the visit number before deleting the database record.
        visit_number = visit.visit_number

        visit.delete()

        messages.success(
            request,
            f"Visit {visit_number} was deleted successfully.",
        )

        return redirect("participants:visit_list")

    return render(
        request,
        "participants/delete_visit.html",
        {
            "visit": visit,
            "participant": participant,
            "study": study,
        },
    )
