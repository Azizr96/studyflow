"""Define forms used for account registration."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    """Provide a registration form for creating new user accounts."""

    email = forms.EmailField(required=True)

    class Meta:
        """Define the model and fields used by the registration form."""

        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        """Validate that the submitted email address is unique."""
        email = self.cleaned_data.get("email")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email
