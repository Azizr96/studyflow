from datetime import date

from django import forms

from .models import Participant, Visit


class ParticipantForm(forms.ModelForm):

    class Meta:
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
        participant_number = self.cleaned_data.get(
            "participant_number"
        )

        if participant_number:
            participant_number = (
                participant_number.strip().upper()
            )

        return participant_number

    def clean(self):
        cleaned_data = super().clean()

        date_of_birth = cleaned_data.get(
            "date_of_birth"
        )
        enrolled_date = cleaned_data.get(
            "enrolled_date"
        )

        if date_of_birth and enrolled_date:
            if enrolled_date <= date_of_birth:
                raise forms.ValidationError(
                    "The enrolled date must be after "
                    "the participant's date of birth."
                )

        return cleaned_data


class VisitForm(forms.ModelForm):

    class Meta:
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
        super().__init__(*args, **kwargs)
        self.participant = participant

    def clean_visit_number(self):
        visit_number = self.cleaned_data.get("visit_number")

        if self.participant and visit_number:
            existing_visit = Visit.objects.filter(
                participant=self.participant,
                visit_number=visit_number,
            )

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
        cleaned_data = super().clean()

        scheduled_date = cleaned_data.get("scheduled_date")
        actual_date = cleaned_data.get("actual_date")
        status = cleaned_data.get("status")

        if actual_date and scheduled_date:
            if actual_date < scheduled_date:
                raise forms.ValidationError(
                    "The actual visit date cannot be before "
                    "the scheduled date."
                )

        if status == Visit.Status.COMPLETED and not actual_date:
            raise forms.ValidationError(
                "A completed visit must have an actual visit date."
            )

        return cleaned_data
