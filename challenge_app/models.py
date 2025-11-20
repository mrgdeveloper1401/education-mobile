from django.db import models
from django.utils.translation import gettext_lazy as _

from core_app.models import CreateMixin, UpdateMixin, ActiveMixin


class Challenge(CreateMixin, UpdateMixin, ActiveMixin):
    DIFFICULTY_LEVELS = (
        ('easy', _("آسان")),
        ('medium', _("متوسط")),
        ('hard', _("سخت")),
        ('expert', _("حرفه‌ای")),
    )

    STATUS_CHOICES = (
        ('draft', _("پیش‌نویس")),
        ('published', _("منتشر شده")),
        ('archived', _("آرشیو شده")),
    )

    LANGUAGE_CHOICES = (
    ("PY", _("Python")),
    ("JA", "Java"),
    ("html", _("HTML")),
    ("C#", _("C#")),
    ("js", _("JavaScript")),
    ("c++", _("C++")),
    )

    name = models.CharField(_("عنوان چالش"), max_length=100)
    # slug = models.SlugField(_("اسلاگ"), max_length=100, unique=True)
    description = models.TextField(_("شرح چالش"))
    language = models.CharField(_("زبان برنامه‌نویسی"), max_length=50, choices=LANGUAGE_CHOICES)
    level = models.CharField(_("سطح"), max_length=10, choices=DIFFICULTY_LEVELS)
    status = models.CharField(_("وضعیت"), max_length=20, choices=STATUS_CHOICES, default='draft')

    # آمار و ارقام
    success_percent = models.FloatField(_("درصد موفقیت"), default=0)
    total_submissions = models.IntegerField(_("تعداد کل ارسال‌ها"), default=0)
    successful_submissions = models.IntegerField(_("تعداد ارسال‌های موفق"), default=0)
    avg_completion_time = models.FloatField(_("میانگین زمان حل (ثانیه)"), default=0)

    # محدودیت‌ها
    time_limit = models.IntegerField(_("محدودیت زمان (میلی‌ثانیه)"), default=2000)
    memory_limit = models.IntegerField(_("محدودیت حافظه (مگابایت)"), default=256)

    # امتیاز و پاداش
    points = models.IntegerField(_("امتیاز"), default=10)
    coins = models.IntegerField(_("سکه پاداش"), default=0)

    # مرتبط‌سازی
    image = models.ForeignKey(
        "core_app.Photo",
        on_delete=models.PROTECT,
        related_name="challenges",
        verbose_name=_("عکس"),
        null=True,
        blank=True
    )
    # ترتیب نمایش
    order = models.IntegerField(_("ترتیب نمایش"), default=0, db_default=0)

    class Meta:
        db_table = "challenge"
        ordering = ("id",)
        verbose_name = _("چالش")
        verbose_name_plural = _("چالش‌ها")


class TestCase(CreateMixin, UpdateMixin, ActiveMixin):
    """تست‌کیس‌های هر چالش"""
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.PROTECT,
        related_name='test_cases',
        verbose_name=_("چالش")
    )
    input_data = models.CharField(_("ورودی"), max_length=500)
    expected_output = models.CharField(_("خروجی مورد انتظار"), max_length=500)
    order = models.IntegerField(_("ترتیب"), default=0)

    class Meta:
        db_table = "test_case"
        verbose_name = _("تست‌کیس")
        verbose_name_plural = _("تست‌کیس‌ها")
        ordering = ("id",)


class ChallengeSubmission(CreateMixin, UpdateMixin, ActiveMixin):
    """مدل برای ذخیره ارسال‌های کاربران"""

    STATUS_CHOICES = (
        ('pending', _("در انتظار")),
        ('running', _("در حال اجرا")),
        ('accepted', _("پذیرفته شده")),
        ('wrong_answer', _("پاسخ اشتباه")),
        ('time_limit_exceeded', _("محدودیت زمان")),
        ('memory_limit_exceeded', _("محدودیت حافظه")),
        ('runtime_error', _("خطای زمان اجرا")),
        ('compilation_error', _("خطای کامپایل")),
    )

    user = models.ForeignKey(
        'auth_app.User',
        on_delete=models.PROTECT,
        related_name='challenge_submissions',
        verbose_name=_("کاربر")
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.PROTECT,
        related_name='submissions',
        verbose_name=_("چالش")
    )
    code = models.TextField(_("کد ارسالی"))
    language = models.CharField(_("زبان برنامه‌نویسی"), max_length=50)
    status = models.CharField(
        _("وضعیت"),
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending'
    )
    execution_time = models.IntegerField(_("زمان اجرا (میلی‌ثانیه)"), null=True, blank=True)
    memory_used = models.IntegerField(_("حافظه استفاده شده (کیلوبایت)"), null=True, blank=True)
    score = models.FloatField(_("امتیاز"), default=0)

    # نتیجه تست‌کیس‌ها (ذخیره به صورت JSON)
    test_results = models.JSONField(_("نتایج تست‌ها"), default=dict, blank=True)

    class Meta:
        db_table = "challenge_submission"
        verbose_name = _("ارسال چالش")
        verbose_name_plural = _("ارسال‌های چالش")
        ordering = ("id",)
        # indexes = [
        #     models.Index(fields=['user', 'challenge']),
        #     models.Index(fields=['status', 'created_at']),
        # ]


class UserChallengeProgress(CreateMixin, UpdateMixin, ActiveMixin):
    """پیشرفت کاربر در هر چالش"""

    user = models.ForeignKey(
        'auth_app.User',
        on_delete=models.PROTECT,
        related_name='challenge_progress',
        verbose_name=_("کاربر")
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.PROTECT,
        related_name='user_progress',
        verbose_name=_("چالش")
    )
    is_completed = models.BooleanField(_("تکمیل شده"), default=False)
    best_score = models.FloatField(_("بهترین امتیاز"), default=0)
    attempts_count = models.IntegerField(_("تعداد تلاش‌ها"), default=0)
    completed_at = models.DateTimeField(_("تاریخ تکمیل"), null=True, blank=True)
    best_submission = models.ForeignKey(
        ChallengeSubmission,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("بهترین ارسال")
    )

    class Meta:
        db_table = "user_challenge_progress"
        verbose_name = _("پیشرفت کاربر در چالش")
        verbose_name_plural = _("پیشرفت‌های کاربران در چالش‌ها")
        unique_together = ('user', 'challenge')
        # indexes = [
        #     models.Index(fields=['user', 'is_completed']),
        # ]

