from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from course_app.models import Category, LessonCourse, Section, SectionVideo


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
            # "for_mobile",
            "course_name",
            "project_counter",
            "course_image",
            "progress",
        )

    @extend_schema_field(serializers.URLField())
    def get_course_image(self, obj):
        return obj.course.course_image.url if obj.course.course_image else None


class SectionLessonCourseSerializer(serializers.ModelSerializer):
    has_access = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = (
            "id",
            "title",
            "cover_image",
            "is_last_section",
            "description",
            "has_access"
        )

    @extend_schema_field(serializers.BooleanField())
    def get_has_access(self, obj):
        return obj.has_access


class SectionVideoSerializer(serializers.ModelSerializer):
    video_field_url = serializers.SerializerMethodField()

    class Meta:
        model = SectionVideo
        fields = ("id", "title", "video_field_url", "video_url", "is_active")

    def get_video_field_url(self, obj):
        return obj.video.url if obj.video else None


class DetailSectionLessonCourseSerializer(serializers.ModelSerializer):
    section_videos = SectionVideoSerializer(many=True, read_only=True)
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
