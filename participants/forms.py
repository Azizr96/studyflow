from django import forms
from .models import Participant


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
                attrs={"type": "date"}
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