from apps.course_app.models import LessonCourse, StudentAccessSection, Section
from apps.auth_app.models import Student


def grant_mobile_sections_access(user_id):
    student = Student.objects.only("id").filter(id=user_id).first()
    if not student:
        return

    course_ids = list(
        LessonCourse.objects.only("course_id")
        .filter(is_active=True)
        .values_list("course_id", flat=True)
    )

    sections = list(
        Section.objects.only("course_id")
        .filter(course_id__in=course_ids, is_active=True)
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

    access_objects = [
        StudentAccessSection(
            student=student,
            section_id=section_id,
            is_access=True
        )
        for section_id in selected_section_ids
    ]

    StudentAccessSection.objects.bulk_create(
        access_objects,
        ignore_conflicts=True
    )
