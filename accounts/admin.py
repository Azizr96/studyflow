from django.contrib import admin
from .models import Role, UserProfile, UserStudy


admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(UserStudy)