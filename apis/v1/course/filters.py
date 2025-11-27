from django_filters.rest_framework import FilterSet

from course_app.models import LessonCourse
from exam_app.models import StudentExamAttempt


class StudentExamAttemptFilter(FilterSet):
    class Meta:
        model = StudentExamAttempt
        fields = {
            "status": ("exact",),
            "is_passed": ("exact",)
        }


class LessonCourseFilter(FilterSet):
    class Meta:
        model = LessonCourse
        fields = {
            "is_free": ("exact",),
            # "progress": ("exact",),
        }
