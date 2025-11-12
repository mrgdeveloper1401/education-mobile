from django.contrib import admin
from .models import Photo, Video


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_size', 'file_format', 'width', 'height', 'is_active')
    list_filter = ('is_active',)
    readonly_fields = ('file_size', 'file_format', 'width', 'height')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_size', 'file_format', 'width', 'height', 'is_active')
    list_filter = ('is_active',)
    readonly_fields = ('file_size', 'file_format', 'width', 'height')
