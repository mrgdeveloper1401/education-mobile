from django.db import models


class CouponEnums(models.TextChoices):
    percent = "percent"
    amount = "amount"
