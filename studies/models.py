from django.contrib.auth.models import User
from django.db import models
from cloudinary_storage.storage import RawMediaCloudinaryStorage

class Study(models.Model):
    protocol_number = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    phase = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.protocol_number} - {self.title}"


class StudyDocument(models.Model):
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
    category = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.study.protocol_number} - {self.file.name}'