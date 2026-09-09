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
]
