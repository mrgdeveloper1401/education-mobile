from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from .models import User, State, City, Coach, Student


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    filter_horizontal = []
    ordering = ("-id",)
    list_display = (
        'mobile_phone',
        'get_full_name',
        'email',
        'is_verified',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at'
    )
    list_filter = (
        'is_verified',
        'is_active',
        'is_staff',
        'is_superuser',
        'gender',
    )
    search_fields = (
        'mobile_phone',
    )
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل استفاده کنید")

    fieldsets = (
        (None, {'fields': ('mobile_phone', 'password')}),
        (_('اطلاعات شخصی'), {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'image',
                'nation_code',
                'birth_date',
                'gender',
                'bio'
            )
        }),
        (_('اطلاعات مکانی'), {
            'fields': (
                'state',
                'city',
                'address'
            )
        }),
        (_('اطلاعات مدرسه'), {
            'fields': ('school',)
        }),
        (_('دسترسی‌ها'), {
            'fields': (
                'is_verified',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': (
                'last_login',
                'created_at',
                'updated_at'
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'mobile_phone',
                'first_name',
                'last_name',
                'email',
                "is_coach",
                'password1',
                'password2',
            ),
        }),
    )

    readonly_fields = ('last_login', 'created_at', 'updated_at')


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_name', "get_city_cont")
    list_display_links = ('state_name',)
    search_fields = ('state_name',)
    list_per_page = 20
    search_help_text = _("برای جست و جو میتوانید از نام استان استفاده کنید")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "state_name",
        ).annotate(
            city_count=Count("cities"),
        )

    def get_city_cont(self, obj):
        return obj.city_count


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_help_text = _("برای جست و جو میتوانید از نام شهر استفاده کنید")
    list_display = ('id', 'city', 'get_state_name')
    list_display_links = ('city',)
    search_fields = ('city', )
    raw_id_fields = ('state',)
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("state").only(
            "city",
            "state__state_name",
        )
    def get_state_name(self, obj):
        return obj.state.state_name


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        'coach_number',
        'get_coach_name',
        'get_coach_phone',
        'created_at'
    )
    search_fields = (
        'coach_number',
        'user__mobile_phone'
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'coach_number',
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').only(
            "user__mobile_phone",
            "user__first_name",
            "user__last_name",
            "coach_number",
            "created_at",
            "updated_at",
        )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        'student_number',
        'student_name',
        'get_student_phone',
        'referral_code',
        'created_at'
    )
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل استفاده کیند")
    search_fields = (
        'user__mobile_phone',
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'student_number',
                'referral_code',
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').only(
            "student_number",
            "referral_code",
            "created_at",
            "updated_at",
            "user__first_name",
            "user__last_name",
            "user__mobile_phone"
        )
