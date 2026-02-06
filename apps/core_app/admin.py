from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Photo, Video, Attachment


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_size', 'file_format', 'width', 'height', 'is_active')
    list_filter = ('is_active',)
    raw_id_fields = ("upload_by",)
    readonly_fields = ('file_size', 'file_format', 'width', 'height')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_size', 'file_format', 'width', 'height', 'is_active')
    list_filter = ('is_active',)
    readonly_fields = ('file_size', 'file_format', 'width', 'height')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "upload_by_id",
        # 'get_file_name',
        'file_type',
        'get_file_size',
        'get_preview',
        'is_active',
        'created_at'
    )
    list_filter = (
        'file_type',
        'is_active',
        'created_at'
    )
    list_display_links = ("id", "file_type", "upload_by_id")
    readonly_fields = (
        'file_size',
        'mime_type',
        'human_readable_size',
        'get_file_preview',
        'created_at',
        'updated_at',
        'get_file_info'
    )
    raw_id_fields = ("upload_by",)
    list_editable = ('is_active',)
    fieldsets = (
        (None, {
            'fields': (
                'file',
                "upload_by",
                'file_type',
            )
        }),
        (_("اطلاعات فایل"), {
            'fields': (
                'get_file_info',
                'file_size',
                'human_readable_size',
                'mime_type',
            )
        }),
        (_("متادیتا"), {
            'fields': (
                'width',
                'height',
                'duration',
            ),
            'classes': ('collapse',)  # قابل جمع شدن
        }),
        (_("پیش‌نمایش"), {
            'fields': (
                'get_file_preview',
            )
        }),
        (_("تنظیمات"), {
            'fields': (
                'is_active',
            )
        }),
        (_("تاریخ‌ها"), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    actions = [
        'make_active',
        'make_inactive',
        'delete_selected_attachments'
    ]

    # def get_file_name(self, obj):
    #     """نمایش نام فایل"""
    #     if obj.file:
    #         filename = obj.file.name.split('/')[-1]
    #         return filename[:50] + "..." if len(filename) > 50 else filename
    #     return "-"

    # get_file_name.short_description = _("نام فایل")
    # get_file_name.admin_order_field = 'file'

    def get_file_size(self, obj):
        """نمایش حجم فایل"""
        return obj.human_readable_size

    get_file_size.short_description = _("حجم فایل")
    get_file_size.admin_order_field = 'file_size'

    def get_preview(self, obj):
        """پیش‌نمایش در لیست"""
        if obj.is_image and obj.file:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 4px;" />',
                obj.file.url
            )
        elif obj.file_type == 'document':
            return format_html(
                '<span style="color: #e74c3c;">📄</span>'
            )
        elif obj.file_type == 'video':
            return format_html(
                '<span style="color: #9b59b6;">🎥</span>'
            )
        elif obj.file_type == 'audio':
            return format_html(
                '<span style="color: #3498db;">🎵</span>'
            )
        elif obj.file_type == 'archive':
            return format_html(
                '<span style="color: #f39c12;">📦</span>'
            )
        else:
            return format_html(
                '<span style="color: #95a5a6;">📎</span>'
            )

    get_preview.short_description = _("پیش‌نمایش")

    def get_file_preview(self, obj):
        """پیش‌نمایش در صفحه ویرایش"""
        if not obj.file:
            return _("فایلی موجود نیست")

        if obj.is_image:
            return format_html(
                '''
                <div style="text-align: center;">
                    <img src="{}" style="max-width: 300px; max-height: 300px; border: 1px solid #ddd; border-radius: 8px; padding: 5px;" />
                    <br/>
                    <a href="{}" target="_blank" style="margin-top: 10px; display: inline-block;">{} {}</a>
                </div>
                ''',
                obj.file.url,
                obj.file.url,
                _("مشاهده فایل اصلی"),
                f"({obj.width}x{obj.height})" if obj.width and obj.height else ""
            )

        else:
            file_icons = {
                'video': '🎥',
                'audio': '🎵',
                'document': '📄',
                'archive': '📦',
                'other': '📎'
            }
            icon = file_icons.get(obj.file_type, '📎')

            return format_html(
                '''
                <div style="text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                    <div style="font-size: 48px; margin-bottom: 10px;">{}</div>
                    <a href="{}" target="_blank" style="font-size: 16px;">{} {}</a>
                    <br/>
                    <span style="color: #666; font-size: 14px;">{}</span>
                </div>
                ''',
                icon,
                obj.file.url,
                _("دانلود فایل"),
                f"({obj.human_readable_size})",
                obj.get_file_type_display()
            )

    get_file_preview.short_description = _("پیش‌نمایش فایل")

    def get_file_info(self, obj):
        """نمایش اطلاعات کامل فایل"""
        if not obj.file:
            return _("فایلی موجود نیست")

        info_lines = [
            f"<strong>{_('نام فایل')}:</strong> {obj.file.name.split('/')[-1]}",
            f"<strong>{_('نوع فایل')}:</strong> {obj.get_file_type_display()}",
            f"<strong>{_('حجم فایل')}:</strong> {obj.human_readable_size}",
        ]

        if obj.mime_type:
            info_lines.append(f"<strong>{_('MIME Type')}:</strong> {obj.mime_type}")

        if obj.width and obj.height:
            info_lines.append(f"<strong>{_('ابعاد')}:</strong> {obj.width} × {obj.height} پیکسل")

        if obj.duration:
            info_lines.append(f"<strong>{_('مدت زمان')}:</strong> {obj.duration} ثانیه")

        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-right: 4px solid #007cba;">{}</div>',
            '<br>'.join(info_lines)
        )

    get_file_info.short_description = _("اطلاعات فایل")

    # def has_add_permission(self, request):
    #     """غیرفعال کردن امکان افزودن از طریق ادمین"""
    #     return False

    # اکشن‌های سفارشی
    def make_active(self, request, queryset):
        """فعال کردن پیوست‌های انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(request, _("{} پیوست فعال شدند").format(updated))

    make_active.short_description = _("فعال کردن پیوست‌های انتخاب شده")

    def make_inactive(self, request, queryset):
        """غیرفعال کردن پیوست‌های انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(request, _("{} پیوست غیرفعال شدند").format(updated))

    make_inactive.short_description = _("غیرفعال کردن پیوست‌های انتخاب شده")

    def delete_selected_attachments(self, request, queryset):
        """حذف پیوست‌های انتخاب شده"""
        count = queryset.count()
        for obj in queryset:
            # حذف فایل از storage
            if obj.file:
                obj.file.delete(save=False)
            obj.delete()
        self.message_user(request, _("{} پیوست حذف شدند").format(count))

    delete_selected_attachments.short_description = _("حذف پیوست‌های انتخاب شده")

    # اضافه کردن فیلترهای سفارشی
    class FileTypeFilter(admin.SimpleListFilter):
        title = _('نوع فایل')
        parameter_name = 'file_type'

        def lookups(self, request, model_admin):
            return Attachment.FILE_TYPES

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(file_type=self.value())

    class SizeFilter(admin.SimpleListFilter):
        title = _('حجم فایل')
        parameter_name = 'size'

        def lookups(self, request, model_admin):
            return [
                ('small', _('کوچک (کمتر از 1MB)')),
                ('medium', _('متوسط (1MB - 10MB)')),
                ('large', _('بزرگ (بیشتر از 10MB)')),
            ]

        def queryset(self, request, queryset):
            if self.value() == 'small':
                return queryset.filter(file_size__lt=1024 * 1024)  # < 1MB
            elif self.value() == 'medium':
                return queryset.filter(file_size__gte=1024 * 1024, file_size__lt=10 * 1024 * 1024)  # 1MB - 10MB
            elif self.value() == 'large':
                return queryset.filter(file_size__gte=10 * 1024 * 1024)  # >= 10MB

    # اضافه کردن فیلترهای سفارشی به list_filter
    list_filter = (FileTypeFilter, SizeFilter) + list_filter

    # تغییر ترتیب فیلدها در فرم ویرایش
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:  # در حالت ایجاد جدید
            return [
                (None, {
                    'fields': ('file',)
                })
            ]
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # در حالت ویرایش
            readonly_fields.append('file')  # غیرقابل ویرایش کردن فایل پس از آپلود
        return readonly_fields
