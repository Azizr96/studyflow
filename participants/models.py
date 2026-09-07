from django.db import models
from studies.models import Study

class Participant(models.Model):

    class Sex(models.TextChoices):
          MALE = "Male", "Male"
          FEMALE = "Female", "Female"
          

    class Status(models.TextChoices):
          SCREENING = "Screening", "Screening"
          ENROLLED = "Enrolled", "Enrolled"
          ACTIVE = "Active", "Active"
          COMPLETED = "Completed", "Completed"
          WITHDRAWN = "Withdrawn", "Withdrawn"
          SCREEN_FAILED = "Screen Failed", "Screen Failed"



    study = models.ForeignKey(
      Study,
      on_delete=models.CASCADE,
      related_name='participants'
    )
    participant_number = models.CharField(
      max_length=50,
      unique=True,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    sex = models.CharField(
          max_length=10,
          choices=Sex.choices,
      )

    status = models.CharField(
          max_length=50,
          choices=Status.choices,
      )
    enrolled_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
          return (
              f"{self.participant_number} - "
              f"{self.first_name} {self.last_name}"
          )
