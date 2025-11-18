from django.db import models
from django.utils.translation import gettext_lazy as _

from core_app.models import CreateMixin, UpdateMixin, ActiveMixin


class SubscriptionPlan(CreateMixin, UpdateMixin, ActiveMixin):
    DURATION_CHOICES = [
        (1, _("۱ ماهه")),
        (2, _("۲ ماهه")),
        (3, _("۳ ماهه")),
        (6, _("۶ ماهه")),
        (12, _("۱۲ ماهه")),
    ]

    name = models.CharField(_("نام پلن"), max_length=100)
    duration = models.IntegerField(_("مدت زمان (ماه)"), choices=DURATION_CHOICES)
    original_price = models.BigIntegerField(_("قیمت اصلی (تومان)"))
    discounted_price = models.BigIntegerField(_("قیمت با تخفیف (تومان)"))
    image = models.ForeignKey(
        'core_app.Photo',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("عکس پلن")
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

    class Meta:
        db_table = 'user_subscription'
        verbose_name = _("اشتراک کاربر")
        verbose_name_plural = _("اشتراک‌های کاربران")
        ordering = ('id',)
