from django.contrib.auth.models import User
from django.db import models
from studies.models import Study


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_admin = models.BooleanField(default=False)
    can_approve_users = models.BooleanField(default=False)
    can_manage_studies = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class UserStudy(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="study_assignments",
    )
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="user_assignments",
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_studies",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "study"],
                name="unique_user_study_assignment",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.study.protocol_number}"