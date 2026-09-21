"""Register study and study document models with the Django admin site."""

from django.contrib import admin
from .models import Study, StudyDocument


admin.site.register(Study)
admin.site.register(StudyDocument)
