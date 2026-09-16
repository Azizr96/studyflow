from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        user=request.user,
    ).order_by("-created_at")

    unread_count = notifications.filter(
        is_read=False,
    ).count()

    context = {
        "notifications": notifications,
        "unread_count": unread_count,
    }

    return render(
        request,
        "notifications/notification_list.html",
        context,
    )


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user,
    )

    if request.method == "POST":
        notification.is_read = True
        notification.save()

        messages.success(
            request,
            "Notification marked as read.",
        )

    return redirect("notifications:notification_list")


@login_required
def mark_all_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(
            is_read=True
        )

        messages.success(
            request,
            "All notifications have been marked as read."
        )

    return redirect("notifications:notification_list")
