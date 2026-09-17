from django.test import TestCase

from .forms import StudyForm


class StudyFormTests(TestCase):
    """Tests for StudyFlow study form validation."""

    def test_end_date_before_start_date_is_rejected(self):
        """A study end date cannot be before its start date."""
        form = StudyForm(
            data={
                "protocol_number": "SF-001",
                "title": "Test Clinical Study",
                "description": "Test study description.",
                "phase": "Phase 2",
                "status": "Planning",
                "start_date": "2026-09-10",
                "end_date": "2026-09-01",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "The end date cannot be before the start date.",
            form.non_field_errors(),
        )

    def test_valid_study_dates_are_accepted(self):
        """A study end date after its start date should be valid."""
        form = StudyForm(
            data={
                "protocol_number": "SF-002",
                "title": "Valid Clinical Study",
                "description": "Test study description.",
                "phase": "Phase 2",
                "status": "Planning",
                "start_date": "2026-09-01",
                "end_date": "2026-09-30",
            }
        )

        self.assertTrue(form.is_valid())