from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apis.utils.custom_exceptions import VolumeImageExceptions


class MobileRegexValidator(RegexValidator):
    regex = r'^09\d{9}'
    message = _("با 09 شروع شود و یازده رقمی باشد")


class NationCodeRegexValidator(RegexValidator):
    regex = r'\d{10}'
    message = _("شماره ملی باید به صورت عدد باشد یا 10 رقم باشد")


def validate_upload_image_user(value):
    value_size = value.size
    max_size = 1 * (1024 * 1024)
    if value_size > max_size:
        raise VolumeImageExceptions()
    return value
