"""Define account roles, user profiles, and study assignments."""

from django.contrib.auth.models import User
from django.db import models
from studies.models import Study


class Role(models.Model):
    """Represent a user role and its associated permissions."""

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_admin = models.BooleanField(default=False)
    can_approve_users = models.BooleanField(default=False)
    can_manage_studies = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)

    def __str__(self):
        """Return the role name as its string representation."""
        return self.name


class UserProfile(models.Model):
    """Store StudyFlow-specific profile information for a user."""

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
        """Return the associated username as the profile representation."""
        return self.user.username


class UserStudy(models.Model):
    """Represent the assignment of a user to a clinical study."""

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
        """Define database constraints for study assignments."""

        constraints = [
            models.UniqueConstraint(
                fields=["user", "study"],
                name="unique_user_study_assignment",
            )
        ]

    def __str__(self):
        """Return the user and study protocol number for the assignment."""
        return f"{self.user.username} - {self.study.protocol_number}"
