from asgiref.sync import sync_to_async

from course_app.models import LessonCourse, StudentAccessSection, Section
from auth_app.models import Student
from django.db import transaction


async def grant_mobile_sections_access(user_id):
    student = await sync_to_async(Student.objects.only("id").filter)(user_id=user_id)

    if not await student.aexists():
        return
    else:
        course_ids = await sync_to_async(
            lambda: list(
                LessonCourse.objects.only("course_id")
                .filter(is_active=True)
                .values_list("course_id", flat=True)
            )
        )()

        sections = await sync_to_async(
                lambda: list(
                    Section.objects.only("course_id")
                    .filter(course_id__in=course_ids, is_active=True)
                    .order_by("course_id", "id")
        ))()

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

        student = await student.afirst()
        access_objects = [
            StudentAccessSection(student=student, section_id=section_id, is_access=True)
            for section_id in selected_section_ids
        ]

        # async with transaction.atomic():
        await StudentAccessSection.objects.abulk_create(access_objects, ignore_conflicts=True)
