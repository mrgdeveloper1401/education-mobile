from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.discount_app.models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    ordering = ("-id",)
    list_display = (
        "code",
        "id",
        "maximum_use",
        "number_of_uses",
        "valid_from",
        "valid_to",
        "coupon_type",
        "amount",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("code",)
    list_per_page = 20
    list_editable = ("is_active", "maximum_use", "number_of_uses", "amount", "coupon_type")
    search_help_text = _("برای جست و جو میتوانید از کد استفاده کنید")
