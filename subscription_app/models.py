from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core_app.models import CreateMixin, UpdateMixin, ActiveMixin
from subscription_app.managers import SubManager


class SubscriptionPlan(CreateMixin, UpdateMixin, ActiveMixin):
    DURATION_CHOICES = [
        (1, _("۱ ماهه")),
        (2, _("۲ ماهه")),
        (3, _("۳ ماهه")),
        (6, _("۶ ماهه")),
        (12, _("۱۲ ماهه")),
    ]
    has_installment = models.BooleanField(_("امکان خرید قسطی"), default=False)
    name = models.CharField(_("نام پلن"), max_length=100)
    duration = models.IntegerField(_("مدت زمان (ماه)"), choices=DURATION_CHOICES)
    original_price = models.BigIntegerField(_("قیمت اصلی (تومان)"))
    discounted_price = models.BigIntegerField(_("قیمت با تخفیف (تومان)"), default=0)
    image = models.ForeignKey(
        'core_app.Photo',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("عکس پلن")
    )
    min_installment_months = models.IntegerField(
        _("حداقل مدت برای قسطی (ماه)"),
        db_default=0,
        default=0,
        validators=[MinValueValidator(0)]
    )
    max_installments = models.IntegerField(
        _("حداکثر تعداد اقساط مجاز"),
        db_default=0,
        default=0,
        validators=[MinValueValidator(0)]
    )

    # ویژگی‌های پلن
    # can_download = models.BooleanField(_("امکان دانلود"), default=False)
    # can_stream_hd = models.BooleanField(_("پخش HD"), default=False)
    # max_devices = models.IntegerField(_("تعداد دستگاه همزمان"), default=1)
    # ad_free = models.BooleanField(_("بدون تبلیغات"), default=False)
    # offline_access = models.BooleanField(_("دسترسی آفلاین"), default=False)
    # exclusive_content = models.BooleanField(_("محتوای اختصاصی"), default=False)
    # priority_support = models.BooleanField(_("پشتیبانی ویژه"), default=False)

    class Meta:
        db_table = 'subscription_plan'
        verbose_name = _("پلن اشتراک")
        verbose_name_plural = _("پلن‌های اشتراک")
        ordering = ('id',)


class UserSubscription(CreateMixin, UpdateMixin, ActiveMixin):
    STATUS_CHOICES = [
        ('active', _("فعال")),
        ('expired', _("منقضی شده")),
        ('canceled', _("لغو شده")),
        ("reserve", _("رزو شده"))
    ]

    user = models.ForeignKey(
        'auth_app.User',
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_("کاربر")
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        verbose_name=_("پلن اشتراک")
    )
    start_date = models.DateTimeField(_("تاریخ شروع"))
    end_date = models.DateTimeField(_("تاریخ پایان"))
    status = models.CharField(
        _("وضعیت"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    transaction_id = models.CharField(
        _("شناسه تراکنش"),
        max_length=100,
        blank=True,
        null=True
    )

    objects = SubManager()

    class Meta:
        db_table = 'user_subscription'
        verbose_name = _("اشتراک کاربر")
        verbose_name_plural = _("اشتراک‌های کاربران")
        ordering = ('id',)


class InstallmentPlan(CreateMixin, UpdateMixin, ActiveMixin):
    """مدل برای انواع طرح‌های قسطی"""

    PLAN_TYPE_CHOICES = [
        ('fixed', _("قسط ثابت")),
        ('variable', _("قسط متغیر")),
    ]

    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='installment_plans',
        verbose_name=_("پلن اشتراک"),
        limit_choices_to={"has_installment": True}
    )
    name = models.CharField(_("نام طرح قسطی"), max_length=100)
    plan_type = models.CharField(
        _("نوع طرح"),
        max_length=20,
        choices=PLAN_TYPE_CHOICES,
        default='fixed'
    )
    number_of_installments = models.IntegerField(
        _("تعداد اقساط"),
        default=1,
        db_default=1,
        validators=[MinValueValidator(0)]
    )
    interest_rate = models.DecimalField(
        _("نرخ سود (درصد)"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        db_table = 'installment_plan'
        verbose_name = _("طرح قسطی")
        verbose_name_plural = _("طرح‌های قسطی")
        ordering = ('id',)


class InstallmentOption(CreateMixin, UpdateMixin, ActiveMixin):
    """گزینه‌های قسطی برای هر پلن"""

    installment_plan = models.ForeignKey(
        InstallmentPlan,
        on_delete=models.PROTECT,
        related_name='options',
        verbose_name=_("طرح قسطی")
    )
    installment_number = models.IntegerField(_("شماره قسط"))
    amount = models.BigIntegerField(_("مبلغ قسط (تومان)"))
    due_days = models.IntegerField(_("تعداد روز تا سررسید"))

    class Meta:
        db_table = 'installment_option'
        verbose_name = _("گزینه قسط")
        verbose_name_plural = _("گزینه‌های قسط")
        ordering = ('id',)
        unique_together = ('installment_plan', 'installment_number')


class UserInstallment(CreateMixin, UpdateMixin):
    """قسط‌های کاربران"""

    STATUS_CHOICES = [
        ('pending', _("در انتظار")),
        ('paid', _("پرداخت شده")),
        ('overdue', _("معوقه")),
        ('failed', _("ناموفق")),
    ]

    user_subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.PROTECT,
        related_name='installments',
        verbose_name=_("اشتراک کاربر")
    )
    installment_option = models.ForeignKey(
        InstallmentOption,
        on_delete=models.PROTECT,
        verbose_name=_("گزینه قسط")
    )
    installment_number = models.IntegerField(_("شماره قسط"))
    amount = models.BigIntegerField(_("مبلغ قسط (تومان)"))
    due_date = models.DateTimeField(_("تاریخ سررسید"))
    paid_date = models.DateTimeField(_("تاریخ پرداخت"), null=True, blank=True)
    status = models.CharField(
        _("وضعیت"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    transaction_id = models.CharField(
        _("شناسه تراکنش"),
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'user_installment'
        verbose_name = _("قسط کاربر")
        verbose_name_plural = _("قسط‌های کاربران")
        ordering = ('id',)