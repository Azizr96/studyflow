"""Define forms and validation for studies and study documents."""

from django import forms
from .models import Study, StudyDocument


class StudyForm(forms.ModelForm):
    """Provide a form for creating clinical studies."""

    class Meta:
        """Define the model, fields, and widgets used by the study form."""

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
        """Validate that the study end date is not before its start date."""
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # A study cannot finish before the date it begins.
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    "The end date cannot be before the start date."
                )

        return cleaned_data


class StudyDocumentForm(forms.ModelForm):
    """Provide a form for uploading documents to a study."""

    class Meta:
        """Define the model and fields used by the document form."""

        model = StudyDocument
        fields = [
            "file",
            "category",
            "version",
        ]

    def clean_file(self):
        """Validate the uploaded document type and file size."""
        uploaded_file = self.cleaned_data.get("file")

        if not uploaded_file:
            return uploaded_file

        # Only allow the document formats supported by StudyFlow.
        allowed_extensions = [
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
        ]

        # Convert the filename to lowercase so extension checks
        # also work with uppercase file extensions.
        file_name = uploaded_file.name.lower()

        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            raise forms.ValidationError(
                "Only PDF, Word, and Excel documents are allowed."
            )

        # Convert 10 MB into bytes before comparing it with the file size.
        max_file_size = 10 * 1024 * 1024

        if uploaded_file.size > max_file_size:
            raise forms.ValidationError(
                "The file must be 10 MB or smaller."
            )

        return uploaded_file
