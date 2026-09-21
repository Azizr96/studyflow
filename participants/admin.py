"""Register participant and visit models with the Django admin site."""

from django.contrib import admin
from .models import Participant, Visit


admin.site.register(Participant)
admin.site.register(Visit)
