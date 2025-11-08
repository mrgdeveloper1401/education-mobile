from course_app.models import LessonCourse, StudentAccessSection, Section
from auth_app.models import Student
from django.db import transaction


def grant_mobile_sections_access(user_id):
    student = Student.objects.only("id").filter(user_id=user_id)

    if not student.exists():
        return
    else:
        course_ids = LessonCourse.objects.filter(
            for_mobile=True
        ).only("course_id").values_list("course_id", flat=True)

        sections = (
            Section.objects.filter(course_id__in=course_ids, is_publish=True)
            .order_by("course_id", "id")
        )

        selected_section_ids = []
        last_course_id = None
        count = 0

        for s in sections:
            if s.course_id != last_course_id:
                last_course_id = s.course_id
                count = 0
            if count < 2:
                selected_section_ids.append(s.id)
                count += 1

        student = student.first()
        access_objects = [
            StudentAccessSection(student=student, section_id=section_id, is_access=True)
            for section_id in selected_section_ids
        ]

        with transaction.atomic():
            StudentAccessSection.objects.bulk_create(access_objects, ignore_conflicts=True)
