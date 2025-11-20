from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import Challenge, TestCase, ChallengeSubmission, UserChallengeProgress


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1
    fields = ('input_data', 'expected_output', 'order')
    ordering = ('order',)


class ChallengeSubmissionInline(admin.TabularInline):
    model = ChallengeSubmission
    extra = 0
    readonly_fields = ('user', 'language', 'status', 'execution_time', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'language',
        'level',
        'status',
        'success_percent',
        'total_submissions',
        'points',
        'is_active',
        "order",
        "id",
        'created_at'
    )
    list_filter = (
        'language',
        'level',
        'status',
        'is_active',
        'created_at'
    )
    search_help_text = _("برای جست و جو میتوانید از نام چالش استفاده کنید")
    search_fields = ('name',)
    readonly_fields = (
        'success_percent',
        'total_submissions',
        'successful_submissions',
        'avg_completion_time',
        'created_at',
        'updated_at',
        'get_completion_rate'
    )
    list_editable = ('status', 'points', 'is_active')
    # prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {
            'fields': (
                'name',
                # 'slug',
                'description',
                'language',
                'level',
                'status'
            )
        }),
        (_("محدودیت‌ها و امتیاز"), {
            'fields': (
                'time_limit',
                'memory_limit',
                'points',
                'coins'
            )
        }),
        (_("آمار و ارقام"), {
            'fields': (
                'success_percent',
                'total_submissions',
                'successful_submissions',
                'avg_completion_time',
                'get_completion_rate'
            )
        }),
        (_("تنظیمات نمایش"), {
            'fields': (
                'image',
                'order',
                'is_active'
            )
        }),
        (_("تاریخ‌ها"), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    inlines = (TestCaseInline,)
    raw_id_fields = ("image",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('image').only(
            "name",
            "language",
            "level",
            "status",
            "success_percent",
            "total_submissions",
            "points",
            "order",
            "is_active",
            "created_at",
            "updated_at",
            "successful_submissions",
            "description",
            "time_limit",
            "coins",
            "memory_limit",
            "avg_completion_time",
            "image__image",
            "image__height",
            "image__width",
        )

    def get_completion_rate(self, obj):
        if obj.total_submissions > 0:
            rate = (obj.successful_submissions / obj.total_submissions) * 100
            color = "green" if rate > 50 else "orange" if rate > 25 else "red"
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
                color, rate
            )
        return "-"

    get_completion_rate.short_description = _("نرخ موفقیت")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # برای ویرایش موجود
            readonly_fields.extend(['language'])  # جلوگیری از تغییر زبان پس از ایجاد
        return readonly_fields


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = (
        'challenge',
        'get_input_preview',
        'get_output_preview',
        'order',
        'created_at'
    )
    list_filter = ('challenge__language', 'challenge__level')
    search_fields = ('challenge__name', 'input_data', 'expected_output')
    list_editable = ('order',)

    fieldsets = (
        (None, {
            'fields': (
                'challenge',
                'input_data',
                'expected_output',
                'order'
            )
        }),
        (_("تاریخ‌ها"), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('challenge')

    def get_input_preview(self, obj):
        if len(obj.input_data) > 50:
            return f"{obj.input_data[:50]}..."
        return obj.input_data

    get_input_preview.short_description = _("ورودی")

    def get_output_preview(self, obj):
        if len(obj.expected_output) > 50:
            return f"{obj.expected_output[:50]}..."
        return obj.expected_output

    get_output_preview.short_description = _("خروجی مورد انتظار")


class StatusFilter(admin.SimpleListFilter):
    title = _("وضعیت ارسال")
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return ChallengeSubmission.STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())


@admin.register(ChallengeSubmission)
class ChallengeSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'challenge',
        'language',
        'status',
        'execution_time',
        'score',
        'created_at'
    )
    list_filter = (
        StatusFilter,
        'language',
        'challenge__level',
        'created_at'
    )
    search_fields = (
        'user__username',
        'user__email',
        'challenge__name',
        'code'
    )
    readonly_fields = (
        'user',
        'challenge',
        'code',
        'language',
        'test_results',
        'created_at',
        'updated_at',
        'get_status_color'
    )

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'challenge',
                'language',
                'code'
            )
        }),
        (_("نتایج اجرا"), {
            'fields': (
                'status',
                'get_status_color',
                'execution_time',
                'memory_used',
                'score'
            )
        }),
        (_("نتایج تست‌ها"), {
            'fields': (
                'test_results',
            )
        }),
        (_("تاریخ‌ها"), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'challenge'
        )

    def get_status_color(self, obj):
        status_colors = {
            'accepted': 'green',
            'wrong_answer': 'red',
            'time_limit_exceeded': 'orange',
            'memory_limit_exceeded': 'orange',
            'runtime_error': 'red',
            'compilation_error': 'red',
            'pending': 'blue',
            'running': 'purple',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )

    get_status_color.short_description = _("وضعیت رنگی")

    def has_add_permission(self, request):
        return False  # کاربران نمی‌توانند از طریق ادمین ارسال ایجاد کنند

    def save_model(self, request, obj, form, change):
        # اگر وضعیت تغییر کرد، آمار چالش را بروزرسانی کن
        if change and 'status' in form.changed_data:
            obj.challenge.update_statistics()
        super().save_model(request, obj, form, change)


@admin.register(UserChallengeProgress)
class UserChallengeProgressAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'challenge',
        'is_completed',
        'best_score',
        'attempts_count',
        'completed_at'
    )
    list_filter = (
        'is_completed',
        'challenge__level',
        'challenge__language'
    )
    search_fields = (
        'user__username',
        'user__email',
        'challenge__name'
    )
    readonly_fields = (
        'user',
        'challenge',
        'best_submission',
        'completed_at',
        'created_at',
        'updated_at'
    )

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'challenge',
                'is_completed'
            )
        }),
        (_("آمار پیشرفت"), {
            'fields': (
                'best_score',
                'attempts_count',
                'best_submission',
                'completed_at'
            )
        }),
        (_("تاریخ‌ها"), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'challenge', 'best_submission'
        )

    def has_add_permission(self, request):
        return False  # پیشرفت کاربران به صورت خودکار ایجاد می‌شود


# اضافه کردن اکشن‌های سفارشی
def make_published(modeladmin, request, queryset):
    queryset.update(status='published')


make_published.short_description = _("انتشار چالش‌های انتخاب شده")


def make_draft(modeladmin, request, queryset):
    queryset.update(status='draft')


make_draft.short_description = _("پیش‌نویس کردن چالش‌های انتخاب شده")


def recalculate_statistics(modeladmin, request, queryset):
    for challenge in queryset:
        challenge.update_statistics()


recalculate_statistics.short_description = _("محاسبه مجدد آمار چالش‌ها")

# اضافه کردن اکشن‌ها به ChallengeAdmin
ChallengeAdmin.actions = [make_published, make_draft, recalculate_statistics]


# اضافه کردن فیلترهای پیشرفته
class HighDifficultyFilter(admin.SimpleListFilter):
    title = _("چالش‌های سخت")
    parameter_name = 'high_difficulty'

    def lookups(self, request, model_admin):
        return [
            ('hard_expert', _("سخت و حرفه‌ای")),
            ('easy_medium', _("آسان و متوسط")),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'hard_expert':
            return queryset.filter(level__in=['hard', 'expert'])
        elif self.value() == 'easy_medium':
            return queryset.filter(level__in=['easy', 'medium'])


# اضافه کردن فیلتر به ChallengeAdmin
ChallengeAdmin.list_filter += (HighDifficultyFilter,)