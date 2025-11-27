from django.db import models
from django.utils.translation import gettext_lazy as _

from core_app.models import CreateMixin, UpdateMixin, ActiveMixin


class Gateway(CreateMixin, UpdateMixin, ActiveMixin):
    user = models.ForeignKey(
        "auth_app.User",
        on_delete=models.PROTECT,
        related_name="gateway_user",
    )
    subscription = models.ForeignKey(
        "subscription_app.SubscriptionPlan",
        on_delete=models.PROTECT,
        related_name="gateways",
    )
    is_complete = models.BooleanField(default=False)
    result_gateway = models.PositiveSmallIntegerField(blank=True, null=True)
    message_gateway = models.CharField(max_length=255, blank=True, null=True)
    track_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "gateway"
        ordering = ("id",)
        verbose_name_plural = _("درخواست های پرداخت")
        verbose_name = _("درخواست پرداخت")
