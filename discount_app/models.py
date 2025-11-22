from django.db import models
from django.utils import timezone

from core_app.models import CreateMixin, UpdateMixin, ActiveMixin
from discount_app.enums import CouponEnums


class Coupon(CreateMixin, UpdateMixin, ActiveMixin):
    code = models.CharField(
        max_length=50,
        unique=True
    )
    maximum_use = models.PositiveIntegerField(default=1)
    number_of_uses = models.PositiveIntegerField(default=0)
    # for_first = models.BooleanField(default=False)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    coupon_type = models.CharField(
        choices=CouponEnums.choices,
        default=CouponEnums.percent,
        max_length=7,
    )
    amount = models.CharField(
        max_length=15
    )
    is_active = models.BooleanField(default=True)

    # objects = models.Manager()
    # valid_coupon = managers.ValidCouponManager()

    def is_valid(self):
        use = self.number_of_uses < self.maximum_use
        valid_time = self.valid_to > timezone.now()

        if use and valid_time:
            return True
        else:
            return False

    class Meta:
        ordering = ("id",)
        db_table = "coupon"