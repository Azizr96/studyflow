from django.urls import path
from . import views


app_name = "studies"

urlpatterns = [
    path(
            "",
            views.study_list,
            name="study_list",
        ),
    path(
        "create/",
        views.create_study,
        name="create_study",
    ),
    
]