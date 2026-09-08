from django import forms
from .models import Study


class StudyForm(forms.ModelForm):

    class Meta:
        model = Study
        fields = [
            "protocol_number",
            "title",
            "description",
            "phase",
            "status",
            "start_date",
            "end_date",
        ]
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    "The end date cannot be before the start date."
                )

        return cleaned_data