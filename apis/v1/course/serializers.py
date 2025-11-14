from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from adrf.serializers import ModelSerializer as AdrfModelSerializer

from course_app.models import Category, LessonCourse, Section, SectionVideo
from exam_app.models import SectionExam


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
            "course_name",
            "project_counter",
            "course_image",
            "progress",
        )

    @extend_schema_field(serializers.URLField())
    def get_course_image(self, obj):
        return obj.course.course_image.course_image if obj.course.course_image else None


class SectionLessonCourseSerializer(serializers.ModelSerializer):
    has_access = serializers.SerializerMethodField()
    section_image = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = (
            "id",
            "title",
            "section_image",
            "is_last_section",
            "description",
            "has_access"
        )

    @extend_schema_field(serializers.BooleanField())
    def get_has_access(self, obj):
        return obj.has_access

    @extend_schema_field(serializers.URLField())
    def get_section_image(self, obj):
        return obj.cover_image.course_image if obj.cover_image else None


class SectionVideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = SectionVideo
        fields = ("id", "title", "video_url")

    @extend_schema_field(serializers.URLField())
    def get_video_url(self, obj):
        return obj.video.get_video_file_url if obj.video else None


class DetailSectionLessonCourseSerializer(serializers.ModelSerializer):
    section_videos = SectionVideoSerializer(many=True, read_only=True)
    has_access = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = (
            "id",
            "title",
            "description",
            "cover_image_url",
            "is_last_section",
            "section_videos",
            "has_access",
        )

    @extend_schema_field(serializers.BooleanField())
    def get_has_access(self, obj):
        return obj.has_access

    @extend_schema_field(serializers.URLField())
    def get_cover_image_url(self ,obj):
        return obj.cover_image.course_image if obj.cover_image else None


class SectionExamSerializer(AdrfModelSerializer):
    class Meta:
        model = SectionExam
        fields = (
            "id",
            "title",
            "description",
            "exam_type",
            'total_score',
            "passing_score",
            "time_limit"
        )
