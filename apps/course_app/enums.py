from django.db import models
from django.utils.translation import gettext_lazy as _


class ProgresChoices(models.TextChoices):
    not_started = "not_started", _("Not Started")
    finished = "finished", _("Finished")
    in_progress = "in_progress", _("In Progress")


class StudentStatusEnum(models.TextChoices):
    active = "active", _("فعال")
    cancel = "cancel", _("انصراف")
    not_paid = "not_paid", _("پرداخت نکرده")


class SectionFileType(models.TextChoices):
    main = "main", _("تمرین اصلی")
    more_then = "more", _("تمرین اضافی")
    # gold = "gold", _("طلایی")


class SendFileChoices(models.TextChoices):
    rejected = "rejected", _("رد شده")
    accept_to_wait = "accept_to_wait", _("در انتظا تایید")
    accepted = "accepted", _("تایید شده")