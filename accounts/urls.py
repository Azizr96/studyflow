from django.urls import path
from . import views


app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("pending-users/", views.pending_users, name="pending_users"),
    path(
        "approve-user/<int:user_id>/",
        views.approve_user,
        name="approve_user",
    ),
    path(
        "reject-user/<int:user_id>/",
        views.reject_user,
        name="reject_user",
    ),
]