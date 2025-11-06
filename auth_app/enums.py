from django.db import models
from django.utils.translation import gettext_lazy as _


class Grade(models.TextChoices):
    one = 'one', _("اول")
    two = 'two', _("دوم")
    three = 'three', _("سوم")
    four = 'four', _("چهارم")
    five = 'five', _("پنجم")
    six = 'six', _("ششم")
    seven = 'seven', _("هفتم")
    eight = 'eight', _("هشتم")
    nine = 'nine', _("نهم")
    ten = 'ten', _("دهم")
    eleven = 'eleven', _("یازدهم")
    twelfth = 'twelfth', _("دوازدهم")
    graduate = 'graduate', _("فارغ التحصیل")
