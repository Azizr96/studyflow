from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import StudyForm
from .models import Study

def can_manage_studies(user):
    if not user.is_authenticated:
        return False

    if not hasattr(user, "profile"):
        return False

    if not user.profile.role:
        return False

    return user.profile.role.can_manage_studies


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
    if not can_manage_studies(request.user):
        messages.error(
            request,
            "You do not have permission to view all studies.",
        )
        return redirect("accounts:login")

    studies = Study.objects.all().order_by("protocol_number")

    context = {
        "studies": studies,
    }

    return render(
        request,
        "studies/study_list.html",
        context,
    )