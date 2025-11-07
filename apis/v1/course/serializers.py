from rest_framework import serializers

from course_app.models import Course, Category, LessonCourse


class ListDetailCourseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.category_name", read_only=True)

    class Meta:
        model = Course
        exclude = (
            "is_deleted",
            "deleted_at"
        )


class ListCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "category_name",
        )


class ListLessonCourseSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    course_image = serializers.SerializerMethodField()
    project_counter = serializers.IntegerField(source="course.project_counter", read_only=True)

    class Meta:
        model = LessonCourse
        fields = (
            "id",
            "class_name",
            "progress",
            "course_name",
            "course_image",
            "project_counter",
        )

    def get_course_image(self, obj):
        return obj.course.course_image.url if obj.course.course_image else None
