from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):

    class Type(models.TextChoices):
        VISIT_REMINDER = "Visit Reminder", "Visit Reminder"
        PARTICIPANT_ADDED = "Participant Added", "Participant Added"
        DOCUMENT_UPLOADED = "Document Uploaded", "Document Uploaded"
        VISIT_COMPLETED = "Visit Completed", "Visit Completed"
        STUDY_ASSIGNED = "Study Assigned", "Study Assigned"
        GENERAL = "General", "General"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    type = models.CharField(
        max_length=50,
        choices=Type.choices,
        default=Type.GENERAL,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
