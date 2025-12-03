from django.contrib import admin
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from mptt.admin import DraggableMPTTAdmin

from exam_app.models import SectionExam
from .models import (
    Category, Course, LessonCourse, StudentEnrollment,
    Section, SectionVideo, StudentAccessSection, CategoryComment
)


class SectionExamInline(admin.StackedInline):
    model = SectionExam
    extra = 0


@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(Category)
    list_display = (
        'category_name',
        'get_depth_display',
        'is_active',
        'created_at'
    )
    search_help_text = _("برای جست و جو میتوانید از نام دسته بندی استفاده کنید")
    raw_id_fields = ("image",)
    list_filter = ('is_active', 'created_at')
    search_fields = ('category_name', )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': (
                'category_name',
                'image',
                'description',
                'description_slug',
                'is_active'
            )
        }),
        (_('ساختار درختی'), {
            'fields': ('_position', '_ref_node_id')
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_depth_display(self, obj):
        return f"سطح {obj.get_depth()}"

    get_depth_display.short_description = _('سطح')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'course_name',
        'category_id',
        "id",
        'is_active',
        'project_counter',
        'created_at'
    )
    list_filter = (
        'is_active',
        'category',
        'created_at'
    )
    search_fields = (
        'course_name',
    )
    search_help_text = _("برای جست و جو میتوانید از نام دوره استفاده کنید")
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('category', 'course_image')

    fieldsets = (
        (None, {
            'fields': (
                'category',
                'course_name',
                'course_description',
                'description_slug',
                'course_image'
            )
        }),
        (_('تنظیمات دوره'), {
            'fields': (
                'is_active',
                'project_counter',
                'course_level',
                'time_course',
                'course_age'
            )
        }),
        (_('امکانات'), {
            'fields': ('facilities',)
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category", "course_image").only(
            "course_name",
            "is_active",
            "project_counter",
            "course_level",
            "time_course",
            "course_age",
            "category__category_name",
            "course_image__id",
            "created_at",
            "updated_at",
            "description_slug",
            "course_description",
            "facilities"
        )


class StudentEnrollmentInline(admin.TabularInline):
    model = StudentEnrollment
    extra = 0
    raw_id_fields = ('student',)
    readonly_fields = ('created_at',)


@admin.register(LessonCourse)
class LessonCourseAdmin(admin.ModelAdmin):
    list_display = (
        'class_name',
        # 'progress',
        'is_active',
        "is_free",
        "student_number",
        'created_at'
    )
    list_filter = (
        'is_active',
        "is_free",
        # 'progress',
        'created_at'
    )
    search_fields = (
        'class_name',
    )
    search_help_text = _("برای جست و جو میتواندی از نام کلاس استفاده کیند")
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('course', 'coach')
    inlines = (StudentEnrollmentInline,)
    list_editable = ('is_free', "student_number")
    fieldsets = (
        (None, {
            'fields': (
                'course',
                'class_name',
                'coach',
                'is_active',
                "is_free",
            )
        }),
        # (_('وضعیت کلاس'), {
        #     'fields': (
        #         'progress',
        #     )
        # }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'get_lesson_course_name',
        "get_student_phone",
        'student_status',
        'created_at'
    )
    list_filter = (
        'student_status',
        'created_at'
    )
    list_editable = ("student_status",)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('student', 'lesson_course')

    fieldsets = (
        (None, {
            'fields': (
                'student',
                'lesson_course',
                'student_status'
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_lesson_course_name(self, obj):
        return obj.lesson_course.class_name

    def get_student_phone(self, obj):
        return obj.student.user.mobile_phone

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("lesson_course", "student__user").only(
            "lesson_course__class_name",
            "student__user__mobile_phone",
            "student_status",
            "created_at",
            "updated_at"
        )


class SectionVideoInline(admin.TabularInline):
    model = SectionVideo
    extra = 0
    readonly_fields = ('created_at',)
    raw_id_fields = ("video",)

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'video',
                # 'video_url',
                'is_active'
            )
        }),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'get_course_name',
        'is_last_section',
        'is_active',
        'created_at'
    )
    list_filter = (
        'is_active',
        'is_last_section',
        'course',
        'created_at'
    )
    search_fields = (
        'title',
        'description',
        'course__course_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('course', 'cover_image')
    inlines = (SectionVideoInline, SectionExamInline)

    fieldsets = (
        (None, {
            'fields': (
                'course',
                'title',
                'description',
                'cover_image'
            )
        }),
        (_('تنظیمات سکشن'), {
            'fields': (
                'is_active',
                'is_last_section'
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_course_name(self, obj):
        return obj.course.course_name

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course").only(
            "course__course_name",
            "is_active",
            "created_at",
            "updated_at",
            "is_last_section",
            "title",
            "is_active",
            "cover_image_id",
            "description"
        )


@admin.register(SectionVideo)
class SectionVideoAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_active',
        'created_at'
    )
    list_filter = (
        'is_active',
        'section__course',
        'created_at'
    )
    search_fields = (
        'title',
    )
    search_help_text = _("برای جست و جو میتوانید از عنوان سکشن استفاده کنید")
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('section', "video")

    fieldsets = (
        (None, {
            'fields': (
                'section',
                'title',
                'video',
                'is_active'
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("section").only(
            "title",
            "is_active",
            "created_at",
            "updated_at",
            "section__title",
            "video__video_file"
        )


@admin.register(StudentAccessSection)
class StudentAccessSectionAdmin(admin.ModelAdmin):
    list_display = (
        'get_student_phone',
        'get_section_name',
        "get_course_name",
        "id",
        "section_id",
        'is_access',
        'is_active',
        'created_at'
    )
    list_filter = (
        'is_access',
        'is_active',
        'created_at'
    )
    search_fields = (
        'student__user__mobile_phone',
        'section__title'
    )
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل یا عنوان سکشن استفاده کیند")
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('student', 'section')

    fieldsets = (
        (None, {
            'fields': (
                'student',
                'section',
                'is_access',
                'is_active'
            )
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_student_phone(self, obj):
        return obj.student.user.mobile_phone

    def get_section_name(self, obj):
        return obj.section.title

    def get_course_name(self, obj):
        return obj.section.course.course_name

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("section__course", "student__user").only(
            "student__user__mobile_phone",
            "section__title",
            "section__course__course_name",
            "created_at",
            "updated_at",
            "is_active",
            "is_access",
        )


@admin.register(CategoryComment)
class CategoryCommentAdmin(DraggableMPTTAdmin):
    list_editable = ("is_active", "is_pined")
    # form = movenodeform_factory(CategoryComment)
    raw_id_fields = ("user", "category", "parent")
    list_display = ('user_id', "id", 'category_id', "parent_id", 'is_pined', 'is_active')
    search_fields = ('user__phone',)
    list_filter = ('is_pined', 'is_active')
    list_display_links = ("user_id", 'id', "category_id")
    search_help_text = _("برای جست وجو میتوانید از شماره موبایل کاربر استفاده کنید")
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    list_per_page = 30
    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "user_id",
            "category_id",
            "is_pined",
            "is_active",
            "comment_body",
            "parent_id",
            "tree_id",
            "rght",
            "lft",
            "level",
            "created_at",
            "updated_at",
        )


# اضافه کردن actions به مدل‌ها
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)

make_active.short_description = _("فعال کردن موارد انتخاب شده")

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)

make_inactive.short_description = _("غیرفعال کردن موارد انتخاب شده")
for model_admin in (CourseAdmin, LessonCourseAdmin, SectionAdmin, SectionVideoAdmin, CategoryCommentAdmin):
    model_admin.actions = (make_active, make_inactive)
