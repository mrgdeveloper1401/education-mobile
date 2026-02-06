from django.contrib.postgres.fields import ArrayField
from django.db import models
from treebeard.mp_tree import MP_Node
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


from apps.core_app.models import CreateMixin, UpdateMixin, ActiveMixin
from apps.course_app.enums import StudentStatusEnum


class Category(MP_Node, CreateMixin, UpdateMixin, ActiveMixin):
    category_name = models.CharField(max_length=100, db_index=True)
    node_order_by = ("category_name",)
    image = models.ForeignKey(
        "core_app.Photo",
        related_name="category_images",
        null=True,
        blank=True,
        verbose_name=_("عکس دسته بندی"),
        on_delete=models.PROTECT,
    )
    description = models.CharField(
        _("توضیح در مورد دسته بندی"),
        max_length=500,
        blank=True,
        null=True
    )
    description_slug = models.SlugField(blank=True, null=True, allow_unicode=True)

    class Meta:
        db_table = 'category'


class Course(CreateMixin, UpdateMixin, ActiveMixin):
    category = models.ForeignKey(Category, related_name="course_category", on_delete=models.PROTECT)
    course_name = models.CharField(max_length=100)
    course_description = models.TextField()
    description_slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    course_image = models.ForeignKey(
        "core_app.Photo",
        help_text=_("حداکثر اندازه عکس 1 مگابایت هست"),
        on_delete=models.PROTECT,
    )
    project_counter = models.PositiveSmallIntegerField(null=True)
    facilities = ArrayField(models.CharField(max_length=30), blank=True, null=True)
    course_level = models.CharField(max_length=13, null=True, blank=True)
    time_course = models.CharField(max_length=10, help_text="مدت زمان دوره")
    course_age = models.CharField(max_length=30, help_text="بازه سنی دوره", blank=True)

    class Meta:
        db_table = 'course'
        ordering = ("-id",)


class LessonCourse(CreateMixin, UpdateMixin, ActiveMixin):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="lesson_course",
        verbose_name=_("دوره")
    )
    is_free = models.BooleanField(default=False)
    class_name = models.CharField(help_text=_("نام کلاس"))
    coach = models.ForeignKey(
        "auth_app.Coach",
        on_delete=models.PROTECT,
        related_name="coach_less_course",
        verbose_name=_("مربی")
    )
    students = models.ManyToManyField(
        "auth_app.Student",
        related_name="student_lesson_course",
        through="StudentEnrollment",
        verbose_name=_("دانش جو")
    )
    # progress = models.CharField(
    #     help_text=_("وضعیت پیشرفت کلاس"),
    #     choices=ProgresChoices.choices,
    #     max_length=11,
    #     default=ProgresChoices.not_started.value
    # )
    # for_mobile = models.BooleanField(default=False)
    student_number = models.PositiveIntegerField(_("تعداد دانشجویان کلاس"), default=0)

    class Meta:
        ordering = ("id",)
        db_table = 'lesson_course'


class StudentEnrollment(CreateMixin, UpdateMixin, ActiveMixin):
    student = models.ForeignKey(
        "auth_app.Student",
        on_delete=models.PROTECT,
        related_name="student_enrollment",
        limit_choices_to={"is_active": True}
    )
    lesson_course = models.ForeignKey(
        LessonCourse,
        on_delete=models.PROTECT,
        related_name="lesson_course_enrollment",
        limit_choices_to={"is_active": True}
    )
    student_status = models.CharField(
        choices=StudentStatusEnum.choices,
        max_length=8,
        default=StudentStatusEnum.active,
    )

    class Meta:
        ordering = ("id",)
        db_table = "lesson_course_students"
        unique_together = ("student", "lesson_course")


class Section(CreateMixin, UpdateMixin, ActiveMixin):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='sections',
        limit_choices_to={"is_active": True},
        verbose_name=_("دوره")
    )
    title = models.CharField(_("عنوان درس یا سکشن"), max_length=255)
    description = models.TextField(_("توضیح سکشن"), blank=True, null=True)
    cover_image = models.ForeignKey(
        "core_app.Photo",
        on_delete=models.PROTECT,
        verbose_name=_("عکس"),
        blank=True,
        null=True
    )
    is_last_section = models.BooleanField(
        default=False,
        help_text=_("اگر تیک این مورد خورده باشد یعنی اخرین سکشن برای درس خواهد بود")
    )

    class Meta:
        ordering = ("id",)
        db_table = 'course_section'


class SectionVideo(CreateMixin, UpdateMixin, ActiveMixin):
    title = models.CharField(max_length=50, help_text=_("عنوان"), null=True)
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name='section_videos',
        limit_choices_to={"is_active": True}
    )
    video = models.ForeignKey(
        "core_app.Video",
        on_delete=models.PROTECT,
        related_name='section_videos',
        verbose_name=_("ویدیو"),
        limit_choices_to={"is_active": True}
    )

    class Meta:
        ordering = ("id",)
        db_table = 'course_section_video'


class StudentAccessSection(CreateMixin, UpdateMixin, ActiveMixin):
    student = models.ForeignKey(
        "auth_app.Student",
        on_delete=models.PROTECT,
        related_name="student_access_section",
        limit_choices_to={"is_active": True}
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="student_section",
        limit_choices_to={"is_active": True}
    )
    is_access = models.BooleanField(default=False)

    class Meta:
        ordering = ("id",)
        db_table = "student_access_section"


class CategoryComment(MPTTModel, CreateMixin, UpdateMixin, ActiveMixin):
    user = models.ForeignKey(
        'auth_app.User',
        on_delete=models.PROTECT,
        related_name='user_comments',
        limit_choices_to={"is_active": True},
        verbose_name=_("کاربر")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='category_comments',
        verbose_name=_("دسته بندی")
    )
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    comment_body = models.JSONField(_("متن کامنت"), default=dict)
    is_pined = models.BooleanField(default=False, verbose_name=_("پین شده"))

    class Meta:
        db_table = 'category_comment'
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرها")
        ordering = ("id",)

    class MPTTMeta:
        order_insertion_by = ("id",)


class CommentAttachment(CreateMixin, UpdateMixin, ActiveMixin):
    """مدل برای فایل‌های پیوست کامنت"""
    comment = models.ForeignKey(
        CategoryComment,
        on_delete=models.PROTECT,
        related_name='attachments',
        verbose_name=_("کامنت")
    )
    file = models.ForeignKey(
        "core_app.Attachment",
        on_delete=models.PROTECT,
        related_name='comment_attachments',
        verbose_name=_("فایل")
    )

    class Meta:
        db_table = "comment_attachment"
        verbose_name = _("پیوست کامنت")
        verbose_name_plural = _("پیوست‌های کامنت")
        # ordering = ('id',)
