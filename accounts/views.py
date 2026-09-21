"""Handle account authentication and user management views."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification
from notifications.utils import create_notification
from studies.models import Study

from .forms import RegistrationForm
from .models import Role, UserStudy


def can_manage_users(user):
    """Check whether a user has permission to manage other users."""

    # Check each requirement separately to safely handle users
    # who are not authenticated or do not yet have a role.
    if not user.is_authenticated:
        return False

    if not hasattr(user, "profile"):
        return False

    if not user.profile.role:
        return False

    return user.profile.role.can_manage_users


def register(request):
    """Register a new user account awaiting administrator approval."""

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

            return redirect("accounts:login")

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
    """Display users waiting for account approval."""

    # Only users with user-management permission can access this page.
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

    # Superusers can assign any role, while other managers
    # are limited to non-elevated roles.
    if request.user.is_superuser:
        roles = Role.objects.all()
    else:
        roles = Role.objects.filter(
            is_admin=False,
            can_manage_users=False,
        )

    context = {
        "users": users,
        "roles": roles,
    }

    return render(
        request,
        "accounts/pending_users.html",
        context,
    )


@login_required
def approve_user(request, user_id):
    """Approve a pending user and assign their selected role."""

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

        # Only a Django superuser can assign elevated roles.
        if (
            not request.user.is_superuser
            and (
                role.is_admin
                or role.can_manage_users
                or role.can_manage_studies
                or role.can_approve_users
            )
        ):
            messages.error(
                request,
                "You do not have permission to assign this role.",
            )
            return redirect("accounts:pending_users")

        if user.profile.is_approved:
            messages.info(
                request,
                f"{user.username} has already been approved.",
            )
            return redirect("accounts:pending_users")

        # Store the selected role and allow the user to access StudyFlow.
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
    """Reject a pending registration and remove the user account."""

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
    """Authenticate approved users with an assigned StudyFlow role."""

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

        # StudyFlow requires a profile, approval, and assigned role
        # in addition to Django's normal authentication.
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

        return redirect("dashboard:home")

    return render(
        request,
        "accounts/login.html",
    )


@login_required
def user_logout(request):
    """Log out the current user when a POST request is submitted."""

    if request.method == "POST":
        logout(request)

        messages.success(
            request,
            "You have been logged out successfully.",
        )

    return redirect("accounts:login")


@login_required
def user_list(request):
    """Display and search approved users for authorised managers."""

    if not can_manage_users(request.user):
        messages.error(
            request,
            "You do not have permission to manage users.",
        )
        return redirect("accounts:login")

    search_query = request.GET.get("q", "").strip()

    # Load approved users together with their profile, role, and
    # active study assignments to reduce additional database queries.
    users = User.objects.filter(
        profile__is_approved=True,
    ).select_related(
        "profile",
        "profile__role",
    ).prefetch_related(
        Prefetch(
            "study_assignments",
            queryset=UserStudy.objects.filter(
                is_active=True,
            ).select_related("study"),
            to_attr="active_study_assignments",
        )
    )

    # Search across the main user and role fields when a query is provided.
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(profile__role__name__icontains=search_query)
        )

    pending_users = User.objects.filter(
        profile__is_approved=False,
    ).select_related(
        "profile",
        "profile__role",
    )

    studies = Study.objects.all().order_by("protocol_number")

    context = {
        "users": users,
        "pending_users": pending_users,
        "search_query": search_query,
        "studies": studies,
    }

    return render(
        request,
        "accounts/user_list.html",
        context,
    )


@login_required
def assign_user_to_study(request, user_id):
    """Assign or reactivate a user's assignment to a study."""

    if not can_manage_users(request.user):
        messages.error(
            request,
            "You do not have permission to assign users to studies.",
        )
        return redirect("accounts:user_list")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        study_id = request.POST.get("study")

        if not study_id:
            messages.error(
                request,
                "Please select a study.",
            )
            return redirect(
                "accounts:user_detail",
                user_id=user.id,
            )

        study = get_object_or_404(Study, id=study_id)

        # Reuse an existing assignment where possible instead of
        # creating a duplicate user and study relationship.
        assignment, created = UserStudy.objects.get_or_create(
            user=user,
            study=study,
            defaults={
                "assigned_by": request.user,
                "is_active": True,
            },
        )

        if created:
            # Notify the user when they receive a new study assignment.
            create_notification(
                user=user,
                title="New Study Assignment",
                message=(
                    f"You have been assigned to "
                    f"{study.protocol_number} - {study.title}."
                ),
                notification_type=Notification.Type.STUDY_ASSIGNED,
            )

            messages.success(
                request,
                (
                    f"{user.username} has been assigned "
                    f"to {study.protocol_number}."
                ),
            )

        else:
            if assignment.is_active:
                messages.info(
                    request,
                    (
                        f"{user.username} is already assigned "
                        f"to {study.protocol_number}."
                    ),
                )

            else:
                # Reactivate the existing assignment rather than
                # creating another database record.
                assignment.is_active = True
                assignment.assigned_by = request.user
                assignment.save()

                create_notification(
                    user=user,
                    title="Study Reassigned",
                    message=(
                        f"You have been reassigned to "
                        f"{study.protocol_number} - {study.title}."
                    ),
                    notification_type=Notification.Type.STUDY_ASSIGNED,
                )

                messages.success(
                    request,
                    (
                        f"{user.username} has been reassigned "
                        f"to {study.protocol_number}."
                    ),
                )

    return redirect(
        "accounts:user_detail",
        user_id=user.id,
    )


@login_required
def unassign_user_from_study(request, assignment_id):
    """Deactivate a user's active study assignment."""

    if not can_manage_users(request.user):
        messages.error(
            request,
            "You do not have permission to manage users.",
        )
        return redirect("accounts:user_list")

    assignment = get_object_or_404(
        UserStudy.objects.select_related(
            "user",
            "study",
        ),
        id=assignment_id,
        is_active=True,
    )

    if request.method == "POST":
        user_id = assignment.user.id

        # Keep the assignment record for history but mark it inactive.
        assignment.is_active = False
        assignment.assigned_by = request.user
        assignment.save()

        messages.success(
            request,
            (
                f"{assignment.user.username} has been unassigned "
                f"from {assignment.study.protocol_number}."
            ),
        )

        return redirect(
            "accounts:user_detail",
            user_id=user_id,
        )

    return render(
        request,
        "accounts/unassign_user_from_study.html",
        {
            "assignment": assignment,
        },
    )


@login_required
def delete_user(request, user_id):
    """Delete a user after confirmation and password verification."""

    if not can_manage_users(request.user):
        messages.error(
            request,
            "You do not have permission to delete users.",
        )
        return redirect("accounts:user_list")

    user_to_delete = get_object_or_404(User, id=user_id)

    # Prevent managers from accidentally deleting their own account.
    if user_to_delete == request.user:
        messages.error(
            request,
            "You cannot delete your own account.",
        )
        return redirect("accounts:user_list")

    if request.method == "POST":
        password = request.POST.get("password")
        confirmation = request.POST.get("confirm_delete")

        # Require the word DELETE as an additional safeguard.
        if confirmation != "DELETE":
            messages.error(
                request,
                "Please confirm that you want to delete this user.",
            )
            return redirect(
                "accounts:delete_user",
                user_id=user_to_delete.id,
            )

        # Re-authenticate the current manager before allowing deletion.
        authenticated_user = authenticate(
            request,
            username=request.user.username,
            password=password,
        )

        if authenticated_user is None:
            messages.error(
                request,
                "Your password was incorrect. User was not deleted.",
            )
            return redirect(
                "accounts:delete_user",
                user_id=user_to_delete.id,
            )

        username = user_to_delete.username
        user_to_delete.delete()

        messages.success(
            request,
            f"{username} has been deleted successfully.",
        )

        return redirect("accounts:user_list")

    context = {
        "user_to_delete": user_to_delete,
    }

    return render(
        request,
        "accounts/delete_user.html",
        context,
    )


@login_required
def user_detail(request, user_id):
    """Display a user's details and available study assignments."""

    if not can_manage_users(request.user):
        messages.error(
            request,
            "You do not have permission to manage users."
        )
        return redirect("dashboard:home")

    account = get_object_or_404(
        User.objects.select_related(
            "profile",
            "profile__role",
        ),
        id=user_id,
    )

    # Retrieve only the user's currently active study assignments.
    active_study_assignments = (
        UserStudy.objects
        .filter(
            user=account,
            is_active=True,
        )
        .select_related("study")
        .order_by("study__protocol_number")
    )

    assigned_study_ids = active_study_assignments.values_list(
        "study_id",
        flat=True,
    )

    # Only show studies that are not already actively assigned.
    available_studies = (
        Study.objects
        .exclude(id__in=assigned_study_ids)
        .order_by("protocol_number")
    )

    context = {
        "account": account,
        "active_study_assignments": active_study_assignments,
        "available_studies": available_studies,
    }

    return render(
        request,
        "accounts/user_detail.html",
        context,
    )
