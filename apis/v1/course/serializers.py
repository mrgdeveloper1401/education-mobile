from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from course_app.models import Category, LessonCourse, Section, StudentAccessSection, SectionVideo, SectionFile


class ListCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "category_name",
        )


class ListClassSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    project_counter = serializers.CharField(source="course.project_counter", read_only=True)
    course_image = serializers.SerializerMethodField()
    course_category = serializers.CharField(source="course.category.course_category", read_only=True)

    class Meta:
        model = LessonCourse
        fields = (
            "id",
            "class_name",
            "course_category",
            "for_mobile",
            "course_name",
            "project_counter",
            "course_image",
            "progress",
        )

    @extend_schema_field(serializers.URLField())
    def get_course_image(self, obj):
        return obj.course.course_image.url if obj.course.course_image else None


class SectionLessonCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = (
            "id",
            "title",
            "cover_image",
            "is_last_section",
            "description"
        )


class SectionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVideo
        fields = ("id", "title", "video", "video_url", "is_publish")


class SectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ("id", "title", "zip_file", "file_type", "answer", "is_publish")


class DetailSectionLessonCourseSerializer(serializers.ModelSerializer):
    section_videos = SectionVideoSerializer(many=True, read_only=True)
    section_files = SectionFileSerializer(many=True, read_only=True)
    has_access = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = (
            "id",
            "title",
            "description",
            "cover_image",
            "is_last_section",
            "section_videos",
            "section_files",
            "has_access",
        )

    @extend_schema_field(serializers.BooleanField())
    def get_has_access(self, obj):
        user_id = self.context['request'].user.id
        return obj.student_section.filter(student__user_id=user_id, is_access=True).exists()
