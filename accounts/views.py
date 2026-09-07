from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login
from .forms import RegistrationForm
from .models import Role

def can_manage_users(user):
    if not user.is_authenticated:
        return False

    if not hasattr(user, "profile"):
        return False

    if not user.profile.role:
        return False

    return user.profile.role.can_manage_users


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

@login_required
def pending_users(request):
    if not can_manage_users(request.user):
        messages.error(
            request,
            "You do not have permission to manage users.",
        )
        return redirect("accounts:register")

    
    

    users = User.objects.filter(
        profile__is_approved=False,
    ).select_related(
        "profile",
        "profile__role",
    )

    if request.user.is_superuser:
        roles = Role.objects.all()
    else:
        roles = Role.objects.filter(
            is_admin=False,
            can_manage_users=False,
        )

    context = {
            'users': users,
            'roles': roles,
        }
    return render(
        request,
        "accounts/pending_users.html",
        context,
    )


@login_required
def approve_user(request, user_id):
    if not can_manage_users(request.user):
        messages.error(
            request,
            "You do not have permission to approve users.",
        )
        return redirect("accounts:pending_users")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        role_id = request.POST.get("role")

        if not role_id:
            messages.error(
                request,
                "Please select a role before approving the user.",
            )
            return redirect("accounts:pending_users")

        role = get_object_or_404(Role, id=role_id)

        user.profile.role = role
        user.profile.is_approved = True
        user.profile.save()

        messages.success(
            request,
            f"{user.username} has been approved as {role.name}.",
        )

    return redirect("accounts:pending_users")


@login_required
def reject_user(request, user_id):
    if not can_manage_users(request.user):
        messages.error(
            request,
            "You do not have permission to reject users.",
        )
        return redirect("accounts:pending_users")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = user.username
        user.delete()

        messages.success(
            request,
            f"{username} has been rejected and removed.",
        )

    return redirect("accounts:pending_users")

def user_login(request):
    if request.user.is_authenticated:
        return render(
            request,
            "accounts/login.html",
        )

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(
                request,
                "Invalid username or password.",
            )
            return redirect("accounts:login")

        if not hasattr(user, "profile"):
            messages.error(
                request,
                "Your account is not configured correctly.",
            )
            return redirect("accounts:login")

        if not user.profile.is_approved:
            messages.error(
                request,
                "Your account is awaiting approval.",
            )
            return redirect("accounts:login")

        if not user.profile.role:
            messages.error(
                request,
                "Your account does not have an assigned role.",
            )
            return redirect("accounts:login")

        login(request, user)

        messages.success(
            request,
            f"Welcome back, {user.first_name or user.username}.",
        )

        return redirect("accounts:login")

    return render(
        request,
        "accounts/login.html",
    )