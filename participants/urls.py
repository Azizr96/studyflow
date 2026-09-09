from django.urls import path
from . import views


app_name = "participants"

urlpatterns = [
    path(
        "study/<int:study_id>/add/",
        views.add_participant,
        name="add_participant",
    ),
]