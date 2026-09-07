from django.contrib.auth.models import User
from django.db import models
from cloudinary_storage.storage import RawMediaCloudinaryStorage

class Study(models.Model):

    class Phase(models.TextChoices):
        PHASE_1 = "Phase 1", "Phase 1"
        PHASE_2 = "Phase 2", "Phase 2"
        PHASE_3 = "Phase 3", "Phase 3"
        PHASE_4 = "Phase 4", "Phase 4"

    class Status(models.TextChoices):
        PLANNING = "Planning", "Planning"
        RECRUITING = "Recruiting", "Recruiting"
        ACTIVE = "Active", "Active"
        COMPLETED = "Completed", "Completed"
        SUSPENDED = "Suspended", "Suspended"
        TERMINATED = "Terminated", "Terminated"
        
    protocol_number = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    phase = models.CharField(
        max_length=50,
        choices=Phase.choices,
    )

    status = models.CharField(
        max_length=50,
        choices=Status.choices,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.protocol_number} - {self.title}"


class StudyDocument(models.Model):

    class Category(models.TextChoices):
        PROTOCOL = "Protocol", "Protocol"
        INVESTIGATOR_BROCHURE = (
            "Investigator Brochure",
            "Investigator Brochure",
        )
        INFORMED_CONSENT = "Informed Consent Form", "Informed Consent Form"
        SITE_DOCUMENT = "Site Document", "Site Document"
        TRAINING_DOCUMENT = "Training Document", "Training Document"
        OTHER = "Other", "Other"

    
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_study_documents'
    )
    file = models.FileField(
        upload_to='study_documents/',
        storage=RawMediaCloudinaryStorage(),
    )
    category = models.CharField(
        max_length=100,
        choices=Category.choices,
    )
    version = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.study.protocol_number} - {self.file.name}'