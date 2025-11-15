import os
from imghdr import what
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from core_app.managers import PublishManager


class ActiveMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class CreateMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UpdateMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, editable=False)
    is_deleted = models.BooleanField(editable=False, null=True)

    objects = PublishManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


class Photo(CreateMixin, UpdateMixin, ActiveMixin):
    # فیلدهای اصلی
    image = models.ImageField(
        upload_to='photos/%Y/%m/%d/',
        verbose_name='تصویر',
        width_field='width',
        height_field='height'
    )
    # متادیتا فایل
    file_size = models.PositiveIntegerField(
        verbose_name='حجم فایل (بایت)',
        blank=True,
        null=True
    )
    file_format = models.CharField(
        max_length=10,
        verbose_name='فرمت فایل',
        blank=True
    )
    # ابعاد تصویر
    width = models.PositiveIntegerField(
        verbose_name='عرض',
        blank=True,
        null=True
    )
    height = models.PositiveIntegerField(
        verbose_name='ارتفاع',
        blank=True,
        null=True
    )
    upload_by = models.ForeignKey(
        "auth_app.User",
        related_name='user_photos',
        on_delete=models.PROTECT,
        null=True # TODO, when clean migration remove these filed
    )
    class Meta:
        verbose_name = 'عکس'
        verbose_name_plural = 'عکس‌ها'
        ordering = ('-id',)

    @property
    def course_image(self):
        return self.image.url if self.image else None

    def calc_image_format(self):
        file_format = self.file_format = what(self.image)
        return file_format

    def save(self, *args, **kwargs):
        self.file_size = self.image.size
        self.file_format = self.calc_image_format()
        super().save(*args, **kwargs)


class Video(CreateMixin, UpdateMixin, ActiveMixin):
    # فایل ویدیو
    video_file = models.FileField(
        upload_to="videos/%Y/%m/%d/",
        validators=[FileExtensionValidator(["mp4", "avi", "mov", "wmv"])],
        verbose_name=_("فایل ویدیو"),
        blank=True,
        null=True
    )
    video_url = models.URLField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name=_("لینک ویدیو")
    )

    # متادیتا فایل
    file_size = models.PositiveBigIntegerField(
        verbose_name=_("حجم فایل (بایت)"),
        blank=True,
        null=True
    )
    duration = models.DurationField(
        verbose_name=_("مدت زمان"),
        blank=True,
        null=True
    )
    file_format = models.CharField(
        max_length=10,
        verbose_name=_("فرمت فایل"),
        blank=True
    )

    # ابعاد ویدیو
    width = models.PositiveIntegerField(
        verbose_name=_("عرض"),
        blank=True,
        null=True
    )
    height = models.PositiveIntegerField(
        verbose_name=_("ارتفاع"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("ویدیو")
        verbose_name_plural = _("ویدیوها")
        ordering = ('-id',)
        db_table = "videos"

    def save(self, *args, **kwargs):
        # محاسبه خودکار اطلاعات فایل
        if self.video_file:
            self.file_size = self.video_file.size
            # تشخیص فرمت
            #  TODO, read format file
            self.file_format = os.path.splitext(self.video_file.name)[1].lower().replace('.', '')

        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        """حجم فایل به مگابایت"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    @property
    def duration_minutes(self):
        """مدت زمان به دقیقه"""
        if self.duration:
            total_seconds = self.duration.total_seconds()
            return round(total_seconds / 60, 2)
        return 0

    @property
    def has_file(self):
        """آیا فایل ویدیو دارد؟"""
        return bool(self.video_file)

    @property
    def has_url(self):
        """آیا لینک ویدیو دارد؟"""
        return bool(self.video_url)

    @property
    def get_video_file_url(self):
        return self.video_file.url
