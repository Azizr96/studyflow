"""Configure the accounts application."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configure the accounts application settings."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        """Load account signals when the application is ready."""
        import accounts.signals  # noqa: F401
