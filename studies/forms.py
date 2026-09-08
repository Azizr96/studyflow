from django import forms
from .models import Study, StudyDocument


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


class StudyDocumentForm(forms.ModelForm):

    class Meta:
        model = StudyDocument
        fields = [
            "file",
            "category",
            "version",
        ]

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")

        if not uploaded_file:
            return uploaded_file

        allowed_extensions = [
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
        ]

        file_name = uploaded_file.name.lower()

        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            raise forms.ValidationError(
                "Only PDF, Word, and Excel documents are allowed."
            )

        max_file_size = 10 * 1024 * 1024

        if uploaded_file.size > max_file_size:
            raise forms.ValidationError(
                "The file must be 10 MB or smaller."
            )

        return uploaded_file