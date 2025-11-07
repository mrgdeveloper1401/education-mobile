import uuid
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
from treebeard.mp_tree import MP_Node
from django.utils.translation import gettext_lazy as _

from core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from course_app.enums import ProgresChoices, StudentStatusEnum, SectionFileType, SendFileChoices
from course_app.validators import max_upload_image_validator


class Category(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    category_name = models.CharField(max_length=100, db_index=True)
    node_order_by = ("category_name",)
    image = models.ImageField(upload_to="category_images/%Y/%m/%d", null=True, blank=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    description_slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    is_publish = models.BooleanField(default=True)

    @property
    def sub_category_name(self):
        return self.get_children().values("id", "category_name")

    class Meta:
        managed = False
        db_table = 'category'


class Course(CreateMixin, UpdateMixin, SoftDeleteMixin):
    category = models.ForeignKey(Category, related_name="course_category", on_delete=models.PROTECT)
    course_name = models.CharField(max_length=100, db_index=True)
    course_description = models.TextField()
    description_slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    course_image = models.ImageField(upload_to="course_image/%Y/%m/%d", validators=[max_upload_image_validator],
                                     help_text=_("حداکثر اندازه عکس 1 مگابایت هست"), blank=True)
    is_publish = models.BooleanField(default=True)
    project_counter = models.PositiveSmallIntegerField(null=True)
    # price = models.FloatField(help_text=_("قیمت دوره"), blank=True, null=True)
    is_free = models.BooleanField(default=False)
    facilities = ArrayField(models.CharField(max_length=30), blank=True, null=True)
    course_level = models.CharField(max_length=13, null=True, blank=True)
    time_course = models.CharField(max_length=10, help_text="مدت زمان دوره", blank=True)
    course_age = models.CharField(max_length=30, help_text="بازه سنی دوره", blank=True)
    order_number = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'course'
        ordering = ("-id",)
        constraints = (
            models.UniqueConstraint(fields=("id", "order_number"), name="unique_order_per_course_id"),
        )


class LessonCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="lesson_course")
    class_name = models.CharField(help_text=_("نام کلاس"))
    coach = models.ForeignKey("auth_app.Coach", on_delete=models.PROTECT, related_name="coach_less_course")
    students = models.ManyToManyField(
        "auth_app.Student",
        related_name="student_lesson_course",
        through="StudentEnrollment"
    )
    is_active = models.BooleanField(default=True)
    progress = models.CharField(
        help_text=_("وضعیت پیشرفت کلاس"),
        choices=ProgresChoices,
        max_length=11,
        default=ProgresChoices.not_started,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'lesson_course'


class StudentEnrollment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey(
        "auth_app.Student",
        on_delete=models.PROTECT,
        related_name="student_enrollment",
        limit_choices_to={"is_active": True}
    )
    lesson_course = models.ForeignKey(
        LessonCourse,
        on_delete=models.PROTECT,
        related_name="lesson_course_enrollment"
    )
    student_status = models.CharField(
        choices=StudentStatusEnum.choices,
        max_length=8,
        default=StudentStatusEnum.active,
        blank=True
    )

    class Meta:
        managed = False
        db_table = "lesson_course_students"
        # unique_together = ("student", "lesson_course")


class Section(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='sections',
        limit_choices_to={"is_publish": True}
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(
        upload_to="section_cover_image/%Y/%m/%d",
        null=True,
        validators=[max_upload_image_validator]
    )
    is_publish = models.BooleanField(default=True)
    is_last_section = models.BooleanField(
        default=False,
        help_text=_("اگر تیک این مورد خورده باشد یعنی اخرین سکشن برای درس خواهد بود")
    )

    class Meta:
        managed = False
        db_table = 'course_section'


class SectionVideo(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=50, help_text=_("عنوان"), null=True)
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name='section_videos',
        limit_choices_to={"is_publish": True}
    )
    video = models.FileField(upload_to="section_video/%Y/%m/%d", validators=[FileExtensionValidator(["mp4"])], blank=True)
    video_url = models.CharField(max_length=500, blank=True, null=True)
    is_publish = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'course_section_video'


class SectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(help_text=_("عنوان"), max_length=100, null=True)
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='section_files',
                                limit_choices_to={"is_publish": True})
    zip_file = models.FileField(upload_to="section_file/%Y/%m/%d", validators=[FileExtensionValidator(["zip", "rar"])],
                                blank=True)
    file_type = models.CharField(
        choices=SectionFileType,
        max_length=9,
        null=True
    )
    answer = models.FileField(
        upload_to="answer/section_file/%Y/%m/%d",
        validators=[FileExtensionValidator(["zip", "rar"])],
        blank=True,
        null=True
    )
    is_publish = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "course_section_file"


class StudentAccessSection(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey("auth_app.Student", on_delete=models.PROTECT, related_name="student_access_section",
                                limit_choices_to={"is_active": True})
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="student_section",
                                limit_choices_to={"is_publish": True})
    is_access = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "student_access_section"


class SendSectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):

    def student_send_section_file(instance, filename):
        student_number = instance.student.student_number
        created = instance.created_at
        return f"{student_number}_{created}"

    student = models.ForeignKey(
        "auth_app.Student",
        on_delete=models.PROTECT,
        related_name="send_section_files",
        limit_choices_to={"is_active": True}
    )
    section_file = models.ForeignKey(SectionFile, on_delete=models.PROTECT, related_name='section_files')
    send_file_status = models.CharField(
        choices=SendFileChoices.choices,
        max_length=14,
        help_text=_("وضعیت فایل ارسالی"),
        default=SendFileChoices.accept_to_wait,
        null=True,
        blank=True
    )
    zip_file = models.FileField(
        help_text=_("فایل ارسالی"),
        upload_to=student_send_section_file
    )
    comment_student = models.TextField(help_text=_("توضیحی در مورد تمرین ارسالی"), null=True)
    comment_teacher = models.CharField(max_length=255, help_text=_("توضیح مربی در مورد فایل ارسال شده دانشجو"),
                                       null=True, blank=True)
    score = models.FloatField(
        help_text=_("نمره تکلیف ارسالی"),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        db_table = "send_file"
        managed = False

    def save(self, *args, **kwargs):
        if self.score:
            if self.score >= 60:
                self.send_file_status = SendFileChoices.accepted
            else:
                self.send_file_status = SendFileChoices.rejected
        super().save(*args, **kwargs)


class CertificateTemplate(CreateMixin, UpdateMixin, SoftDeleteMixin):
    template_image = models.ImageField(
        upload_to="certificate_template/%Y/%m/%d",
        validators=(max_upload_image_validator,),
        help_text=_("حداکثر اندازه سایز تمپلیت ۲ مگابایت باشد")
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'certificate_template'


class Certificate(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="section_certificates"
    )
    student = models.ForeignKey(
        "auth_app.Student",
        on_delete=models.PROTECT,
        related_name="student_certificates"
    )
    unique_code = models.CharField(
        max_length=36,
        unique=True,
        blank=True,
        null=True
    )
    qr_code = models.ImageField(
        upload_to="certificates/qr_codes/%Y/%m/%d/",
        blank=True
    )
    final_pdf = models.FileField(
        upload_to="certificates/pdf/%Y/%m/%d/",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        # unique_together = ("section", "student")
        db_table = "course_certificate"
        managed = False

    def save(self, *args, **kwargs):
        if self.unique_code is None and self.pk is None:
            self.unique_code = str(uuid.uuid4())
        super().save(*args, **kwargs)
