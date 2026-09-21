"""Define participant and visit models for clinical studies."""

from django.db import models

from studies.models import Study


class Participant(models.Model):
    """Represent a participant enrolled in a clinical study."""

    class Sex(models.TextChoices):
        """Define the available participant sex choices."""

        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    class Status(models.TextChoices):
        """Define the available participant status choices."""

        SCREENING = "Screening", "Screening"
        ENROLLED = "Enrolled", "Enrolled"
        ACTIVE = "Active", "Active"
        COMPLETED = "Completed", "Completed"
        WITHDRAWN = "Withdrawn", "Withdrawn"
        SCREEN_FAILED = "Screen Failed", "Screen Failed"

    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="participants",
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
        """Return the participant number and full name."""
        return (
            f"{self.participant_number} - "
            f"{self.first_name} {self.last_name}"
        )


class Visit(models.Model):
    """Represent a scheduled or completed visit for a participant."""

    class VisitType(models.TextChoices):
        """Define the available clinical visit types."""

        SCREENING = "Screening", "Screening"
        BASELINE = "Baseline", "Baseline"
        FOLLOW_UP = "Follow Up", "Follow Up"
        UNSCHEDULED = "Unscheduled", "Unscheduled"
        END_OF_STUDY = "End of Study", "End of Study"

    class Status(models.TextChoices):
        """Define the available visit status choices."""

        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        MISSED = "Missed", "Missed"
        CANCELLED = "Cancelled", "Cancelled"

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="visits",
    )
    visit_number = models.PositiveIntegerField()
    visit_type = models.CharField(
        max_length=50,
        choices=VisitType.choices,
    )
    scheduled_date = models.DateField()
    actual_date = models.DateField(
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Define database constraints for participant visits."""

        # Prevent the same visit number being stored twice
        # for a single participant.
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "visit_number"],
                name="unique_participant_visit_number",
            )
        ]

    def __str__(self):
        """Return the participant number and visit number."""
        return (
            f"{self.participant.participant_number} - "
            f"Visit {self.visit_number}"
        )
