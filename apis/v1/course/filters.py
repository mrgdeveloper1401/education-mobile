from django_filters.rest_framework import FilterSet
from exam_app.models import StudentExamAttempt


class StudentExamAttemptFilter(FilterSet):
    class Meta:
        model = StudentExamAttempt
        fields = {
            "status": ("exact",),
            "is_passed": ("exact",)
        }
