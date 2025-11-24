from django.db import models
from django.utils.translation import gettext_lazy as _
from core_app.models import CreateMixin, UpdateMixin, ActiveMixin


class SectionExam(CreateMixin, UpdateMixin, ActiveMixin):
    section = models.ForeignKey(
        "course_app.Section",
        related_name="section_exams",
        on_delete=models.PROTECT,
        verbose_name=_("سکشن"),
        limit_choices_to={"is_active": True}
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("عنوان آزمون")
    )
    description = models.TextField(
        verbose_name=_("توضیحات آزمون"),
        blank=True
    )
    exam_type = models.CharField(
        max_length=20,
        choices=[
            ('quiz', _("کوییز")),
            ('midterm', _("کد")),
        ],
        default='quiz',
        verbose_name=_("نوع آزمون")
    )
    total_score = models.PositiveIntegerField(
        default=100,
        verbose_name=_("نمره کل")
    )
    passing_score = models.PositiveIntegerField(
        default=50,
        verbose_name=_("نمره قبولی")
    )
    # time_limit = models.PositiveIntegerField(
    #     help_text=_("مدت زمان آزمون به دقیقه"),
    #     null=True,
    #     blank=True,
    #     verbose_name=_("مدت زمان")
    # )

    class Meta:
        db_table = 'section_exam'
        ordering = ('id',)
        verbose_name = _("آزمون سکشن")
        verbose_name_plural = _("آزمون‌های سکشن")


class Question(CreateMixin, UpdateMixin, ActiveMixin):
    exam = models.ForeignKey(
        SectionExam,
        related_name="questions",
        on_delete=models.PROTECT,
        verbose_name=_("آزمون")
    )
    question_text = models.JSONField(
        verbose_name=_("متن سوال"),
        default=dict
    )
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('multiple_choice', _("چند گزینه‌ای")),
            ('code', _("کد")),
        ],
        verbose_name=_("نوع سوال")
    )
    score = models.PositiveIntegerField(
        default=1,
        verbose_name=_("نمره سوال")
    )
    display_order = models.PositiveIntegerField(
        default=1,
        verbose_name=_("ترتیب نمایش")
    )
    explanation = models.JSONField(
        verbose_name=_("راهنمایی پاسخ"),
        blank=True,
        null=True
    )
    answer_the_question = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_("پاسخ سوال")
    )
    class Meta:
        db_table = 'exam_question'
        ordering = ('id',)
        verbose_name = _("سوال آزمون")
        verbose_name_plural = _("سوالات آزمون")


class Choice(CreateMixin, UpdateMixin, ActiveMixin):
    question = models.ForeignKey(
        Question,
        related_name="choices",
        on_delete=models.PROTECT,
        verbose_name=_("سوال")
    )
    choice_text = models.CharField(
        max_length=500,
        verbose_name=_("متن گزینه")
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name=_("پاسخ صحیح")
    )

    class Meta:
        db_table = 'exam_choice'
        ordering = ('id',)
        verbose_name = _("گزینه سوال")
        verbose_name_plural = _("گزینه‌های سوال")


class StudentExamAttempt(CreateMixin, UpdateMixin, ActiveMixin):
    student = models.ForeignKey(
        "auth_app.Student",
        related_name="exam_attempts",
        on_delete=models.PROTECT,
        verbose_name=_("دانش‌آموز")
    )
    exam = models.ForeignKey(
        SectionExam,
        related_name="attempts",
        on_delete=models.PROTECT,
        verbose_name=_("آزمون")
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("زمان شروع")
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("زمان تحویل")
    )
    total_score = models.FloatField(
        default=0,
        verbose_name=_("نمره کل")
    )
    obtained_score = models.FloatField(
        default=0,
        verbose_name=_("نمره کسب شده")
    )
    is_passed = models.BooleanField(
        default=False,
        verbose_name=_("قبول شده")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', _("در حال انجام")),
            ('graded', _("تصحیح شده")),
            ("done", _("ازموت تمام شده"))
        ],
        default='in_progress',
        verbose_name=_("وضعیت")
    )

    class Meta:
        db_table = 'student_exam_attempt'
        unique_together = ('student', 'exam')
        verbose_name = _("شرکت در آزمون")
        verbose_name_plural = _("شرکت‌های در آزمون")


class StudentAnswer(CreateMixin, UpdateMixin, ActiveMixin):
    STATUS_CHOICES = (
        ("accepted", _("پذیرفته شده")),
        ("reject", _("رد شده"))
    )

    student = models.ForeignKey(
        "auth_app.Student",
        on_delete=models.PROTECT,
        related_name="student_answers"
    )
    attempt = models.ForeignKey(
        StudentExamAttempt,
        related_name="answers",
        on_delete=models.PROTECT,
        verbose_name=_("شرکت در آزمون")
    )
    question = models.ForeignKey(
        Question,
        related_name="student_answers",
        on_delete=models.PROTECT,
        verbose_name=_("سوال")
    )

    # برای سوالات چندگزینه‌ای
    selected_choices = models.ManyToManyField(
        Choice,
        blank=True,
        verbose_name=_("گزینه‌های انتخاب شده")
    )

    # status for question code
    status = models.CharField(max_length=10, blank=True, null=True, choices=STATUS_CHOICES)

    # نتیجه تصحیح
    score = models.FloatField(
        default=0,
        verbose_name=_("نمره کسب شده")
    )
    teacher_feedback = models.TextField(
        blank=True,
        verbose_name=_("نظر مربی")
    )
    # graded_by = models.ForeignKey(
    #     "auth_app.Coach",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     verbose_name=_("تصحیح کننده")
    # )
    graded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("زمان تصحیح")
    )
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        verbose_name=_("صحیح است")
    )

    class Meta:
        db_table = 'student_exam_answer'
        unique_together = ('attempt', 'question')
        verbose_name = _("پاسخ دانش‌آموز")
        verbose_name_plural = _("پاسخ‌های دانش‌آموزان")


class ExamGrading(CreateMixin, UpdateMixin, ActiveMixin):
    exam = models.ForeignKey(
        SectionExam,
        related_name="gradings",
        on_delete=models.PROTECT,
        verbose_name=_("آزمون")
    )
    student = models.ForeignKey(
        "auth_app.Student",
        related_name="exam_gradings",
        on_delete=models.PROTECT,
        verbose_name=_("دانش‌آموز")
    )
    total_score = models.FloatField(
        verbose_name=_("نمره کل")
    )
    obtained_score = models.FloatField(
        verbose_name=_("نمره کسب شده")
    )
    # percentage = models.FloatField(
    #     verbose_name=_("درصد")
    # )
    grade = models.CharField(
        max_length=5,
        verbose_name=_("نمره")
    )
    feedback = models.TextField(
        blank=True,
        verbose_name=_("نظر کلی")
    )

    class Meta:
        db_table = 'exam_grading'
        unique_together = ('exam', 'student')
        verbose_name = _("تصحیح آزمون")
        verbose_name_plural = _("تصحیح‌های آزمون")
