from django.urls import path
from . import views


app_name = "participants"

urlpatterns = [
    path(
        "",
        views.participant_list,
        name="participant_list",
    ),
    path(
        "study/<int:study_id>/add/",
        views.add_participant,
        name="add_participant",
    ),
    path(
        "<int:participant_id>/update/",
        views.update_participant,
        name="update_participant",
    ),
    path(
        "<int:participant_id>/delete/",
        views.delete_participant,
        name="delete_participant",
    ),
    path(
        "<int:participant_id>/visits/add/",
        views.add_visit,
        name="add_visit",
    ),
    path(
        "visits/",
        views.visit_list,
        name="visit_list",
    ),
    path(
        "visits/<int:visit_id>/update/",
        views.update_visit,
        name="update_visit",
    ),
    path(
        "visits/<int:visit_id>/delete/",
        views.delete_visit,
        name="delete_visit",
    ),
]
