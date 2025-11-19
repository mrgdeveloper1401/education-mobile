from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import SubscriptionPlan, UserSubscription

User = get_user_model()


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display_links = ("id", 'name')
    raw_id_fields = ("image",)
    list_display = (
        'id',
        'name',
        'get_duration_display',
        'original_price_formatted',
        'discounted_price_formatted',
        'discount_percentage',
        'is_active',
        'created_at'
    )

    list_filter = (
        'duration',
        'is_active',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'name',
    )
    search_help_text = _("برای جست و جو کردن میتوانید از نام پلن استفاده کنید")
    readonly_fields = (
        'created_at',
        'updated_at',
        'discount_percentage'
    )

    fieldsets = (
        (_('اطلاعات اصلی'), {
            'fields': (
                'name',
                'duration',
                'original_price',
                'discounted_price',
                'image',
                'is_active'
            )
        }),
        (_('ویژگی‌های پلن'), {
            'fields': (
                'discount_percentage',
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    def original_price_formatted(self, obj):
        return f"{obj.original_price:,} تومان"

    original_price_formatted.short_description = _('قیمت اصلی')

    def discounted_price_formatted(self, obj):
        return f"{obj.discounted_price:,} تومان"

    discounted_price_formatted.short_description = _('قیمت با تخفیف')

    def discount_percentage(self, obj):
        if obj.original_price and obj.original_price > 0:
            percentage = ((obj.original_price - obj.discounted_price) / obj.original_price) * 100
            return f"{percentage:.0f}%"
        return "0%"

    discount_percentage.short_description = _('درصد تخفیف')

    def get_duration_display(self, obj):
        return obj.get_duration_display()

    get_duration_display.short_description = _('مدت زمان')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "plan")
    list_display_links = ("id", "user__mobile_phone", "start_date", "end_date")
    search_help_text = _("برای حست و جو میتوانید از شماره موبایل کاربر استفاده کنید")
    list_display = (
        'id',
        "user__mobile_phone",
        # 'user_link',
        # 'plan_link',
        'start_date',
        'end_date',
        'status_badge',
        'is_active',
        'days_remaining',
        'created_at'
    )

    list_filter = (
        'status',
        'plan__duration',
        'is_active',
        'start_date',
        'end_date',
        'created_at'
    )

    search_fields = (
        'user__mobile_phone',
        # 'plan__name',
        # 'transaction_id'
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'is_subscription_active',
        'days_remaining'
    )

    fieldsets = (
        (_('اطلاعات کاربر و پلن'), {
            'fields': (
                'user',
                'plan',
                'transaction_id'
            )
        }),
        (_('زمان‌بندی'), {
            'fields': (
                'start_date',
                'end_date',
                'status'
            )
        }),
        (_('وضعیت'), {
            'fields': (
                'is_active',
                'is_subscription_active',
                'days_remaining'
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    def user_link(self, obj):
        url = reverse_lazy('admin:auth_app_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.id)

    user_link.short_description = _('کاربر')

    def plan_link(self, obj):
        url = reverse_lazy('admin:subscription_subscriptionplan_change', args=[obj.plan.id])
        return format_html('<a href="{}">{}</a>', url, obj.plan.name)

    plan_link.short_description = _('پلن')

    def status_badge(self, obj):
        status_colors = {
            'active': 'green',
            'expired': 'red',
            'canceled': 'orange'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = _('وضعیت')

    def days_remaining(self, obj):
        if obj.status and obj.end_date:
            if obj.status == 'active' and obj.end_date > timezone.now():
                days = (obj.end_date - timezone.now()).days
                color = "green" if days > 7 else "orange" if days > 3 else "red"
                return format_html(
                    '<span style="color: {}; font-weight: bold;">{} روز</span>',
                    color,
                    days
                )
            return format_html('<span style="color: gray;">-</span>')
        else:
            return None

    days_remaining.short_description = _('روزهای باقی‌مانده')

    def is_subscription_active(self, obj):
        if obj.status and obj.end_date:
            is_active = obj.status == 'active' and obj.end_date > timezone.now()
            badge = '✅ فعال' if is_active else '❌ غیرفعال'
            color = 'green' if is_active else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                badge
            )
        else:
            return None

    is_subscription_active.short_description = _('وضعیت اشتراک')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plan').only(
            "start_date",
            "end_date",
            "transaction_id",
            "is_active",
            "created_at",
            "updated_at",
            "plan__name",
            "plan__duration",
            "user__mobile_phone",
            "status"
        )

    # actions
    actions = ('mark_as_active', 'mark_as_expired', 'mark_as_canceled')

    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} اشتراک با موفقیت فعال شد.')

    mark_as_active.short_description = _('فعال کردن اشتراک‌های انتخاب شده')

    def mark_as_expired(self, request, queryset):
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} اشتراک با موفقیت منقضی شد.')

    mark_as_expired.short_description = _('منقضی کردن اشتراک‌های انتخاب شده')

    def mark_as_canceled(self, request, queryset):
        updated = queryset.update(status='canceled')
        self.message_user(request, f'{updated} اشتراک با موفقیت لغو شد.')

    mark_as_canceled.short_description = _('لغو اشتراک‌های انتخاب شده')
