from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                (
                    "Your account has been created successfully. "
                    "Please wait for administrator approval."
                ),
            )

            return redirect("accounts:register")

    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "accounts/register.html",
        context,
    )