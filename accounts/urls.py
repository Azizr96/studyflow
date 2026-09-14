from django.urls import path
from . import views


app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("pending-users/", views.pending_users, name="pending_users"),
    path("users/", views.user_list, name="user_list"),
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
    path(
        "assign-study/<int:user_id>/",
        views.assign_user_to_study,
        name="assign_user_to_study",
    ),
    path(
        "users/assignments/<int:assignment_id>/remove/",
        views.unassign_user_from_study,
        name="unassign_user_from_study",
    ),
    path(
        "delete-user/<int:user_id>/",
        views.delete_user,
        name="delete_user",
    ),
    path(
        "users/<int:user_id>/",
        views.user_detail,
        name="user_detail",
    ),
]