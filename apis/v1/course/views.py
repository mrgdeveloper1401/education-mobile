from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins, viewsets, permissions, generics

from . import serializers
from course_app.models import Course, Category, LessonCourse
from ...utils.custom_pagination import TwentyPageNumberPagination


class ListDetailCourseView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.ListDetailCourseSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Course.objects.filter(
            is_publish=True
        ).defer(
            "is_deleted",
            "deleted_at"
        ).select_related(
            "category"
        )

    def filter_queryset(self, queryset):
        category_id = self.request.query_params.get("category_id", None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class ListCategoryView(generics.ListAPIView):
    serializer_class = serializers.ListCategorySerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Category.objects.filter(
        is_publish=True
    ).only(
        "category_name",
    )


class LessonCourseView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.ListLessonCourseSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = TwentyPageNumberPagination

    def get_queryset(self):
        if self.action == "list":
            return LessonCourse.objects.select_related("course").filter(is_active=True).only(
                "course__course_name",
                "course__course_image",
                "course__project_counter",
                "class_name",
                "progress"
            )
        return None

    # @method_decorator(cache_page(timeout=60 * 60 * 24, key_prefix="list_lesson_course"))
    # def list(self, request, *args, **kwargs):
    #     response = super().list(request, *args, **kwargs)
    #     return response
