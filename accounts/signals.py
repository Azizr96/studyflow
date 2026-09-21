"""Handle signals for automatically creating user profiles."""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile automatically when a new user is created."""

    # Only create a profile when the User is first created.
    if created:
        UserProfile.objects.create(user=instance)
