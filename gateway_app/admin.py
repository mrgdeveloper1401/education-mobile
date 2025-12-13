from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Gateway, ResultGateway


@admin.register(Gateway)
class GatewayAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "subscription")
    list_display = (
        "id",
        "user_id",
        "get_user_phone",
        "subscription_id",
        "is_complete",
        "track_id",
        "is_active",
        "is_bazaar_pay_payment"
    )
    list_filter = ("is_complete", "is_active")
    list_per_page = 20
    search_fields = ("user__mobile_phone",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل استفاده کنید")
    list_display_links = ("id", "user_id", "subscription_id", "get_user_phone")
    list_editable = ("is_active", "is_complete")

    def get_user_phone(self, obj):
        return obj.user.mobile_phone

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if "gateway_app_gateway_changelist" in request.resolver_match.url_name:
            return qs.select_related("user").only(
                "user__mobile_phone",
                "subscription_id",
                "is_complete",
                "track_id",
                "is_active",
                "checkout_token"
            )
        else:
            return qs


@admin.register(ResultGateway)
class ResultGatewayAdmin(admin.ModelAdmin):
    raw_id_fields = ("gateway",)
    list_display = (
        "id",
        "gateway_id",
        "paid_at",
        "amount",
        "ref_number",
        "order_id",
        "is_active",
        "created_at",
    )
    search_fields = ("gateway__user__mobile_phone",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل کاربر استفاده کنید")
    list_display_links = ("id", "gateway_id", "paid_at")
    list_per_page = 20
    list_filter = ("is_active", "created_at")
