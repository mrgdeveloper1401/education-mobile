from rest_framework import serializers

from course_app.models import Category, LessonCourse, Section


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

    class Meta:
        model = LessonCourse
        fields = (
            "id",
            "class_name",
            "for_mobile",
            "course_name",
            "project_counter",
            "course_image",
        )

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
