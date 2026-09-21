"""Define forms and validation for participants and visits."""

from datetime import date

from django import forms

from .models import Participant, Visit


class ParticipantForm(forms.ModelForm):
    """Provide a form for creating and updating participants."""

    class Meta:
        """Define the model, fields, and widgets used by the form."""

        model = Participant
        fields = [
            "participant_number",
            "first_name",
            "last_name",
            "date_of_birth",
            "sex",
            "status",
            "enrolled_date",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "max": date.today().isoformat(),
                }
            ),
            "enrolled_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def clean_participant_number(self):
        """Remove spaces and convert the participant number to uppercase."""
        participant_number = self.cleaned_data.get(
            "participant_number"
        )

        # Store participant numbers in a consistent uppercase format.
        if participant_number:
            participant_number = (
                participant_number.strip().upper()
            )

        return participant_number

    def clean(self):
        """Validate the participant's date of birth and enrolment date."""
        cleaned_data = super().clean()

        date_of_birth = cleaned_data.get(
            "date_of_birth"
        )
        enrolled_date = cleaned_data.get(
            "enrolled_date"
        )

        # A participant cannot be enrolled before or on their birth date.
        if date_of_birth and enrolled_date:
            if enrolled_date <= date_of_birth:
                raise forms.ValidationError(
                    "The enrolled date must be after "
                    "the participant's date of birth."
                )

        return cleaned_data


class VisitForm(forms.ModelForm):
    """Provide a form for creating and updating participant visits."""

    class Meta:
        """Define the model, fields, and widgets used by the form."""

        model = Visit
        fields = [
            "visit_number",
            "visit_type",
            "scheduled_date",
            "actual_date",
            "status",
            "notes",
        ]

        widgets = {
            "scheduled_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "actual_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, participant=None, **kwargs):
        """Store the participant so visit validation can use it."""
        super().__init__(*args, **kwargs)
        self.participant = participant

    def clean_visit_number(self):
        """Prevent duplicate visit numbers for the same participant."""
        visit_number = self.cleaned_data.get("visit_number")

        if self.participant and visit_number:
            # Check whether this participant already has this visit number.
            existing_visit = Visit.objects.filter(
                participant=self.participant,
                visit_number=visit_number,
            )

            # When editing, exclude the current visit from the duplicate check.
            if self.instance.pk:
                existing_visit = existing_visit.exclude(
                    pk=self.instance.pk,
                )

            if existing_visit.exists():
                raise forms.ValidationError(
                    f"Visit {visit_number} already exists "
                    "for this participant."
                )

        return visit_number

    def clean(self):
        """Validate visit dates and completed visit requirements."""
        cleaned_data = super().clean()

        scheduled_date = cleaned_data.get("scheduled_date")
        actual_date = cleaned_data.get("actual_date")
        status = cleaned_data.get("status")

        # The actual visit cannot take place before its scheduled date.
        if actual_date and scheduled_date:
            if actual_date < scheduled_date:
                raise forms.ValidationError(
                    "The actual visit date cannot be before "
                    "the scheduled date."
                )

        # Completed visits must record the date they actually occurred.
        if status == Visit.Status.COMPLETED and not actual_date:
            raise forms.ValidationError(
                "A completed visit must have an actual visit date."
            )

        return cleaned_data
