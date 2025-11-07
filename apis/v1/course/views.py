from rest_framework import mixins, viewsets, permissions, generics

from . import serializers
from course_app.models import Course, Category, LessonCourse, Section
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


class ListLessonClassView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.ListClassSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = TwentyPageNumberPagination

    def get_queryset(self):
        return LessonCourse.objects.filter(
            is_active=True,
            for_mobile=True
        ).select_related("course").only(
            "course__course_name",
            "course__project_counter",
            "course__course_image",
            "for_mobile",
            "class_name"
        )


class SectionLessonCourseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.SectionLessonCourseSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Section.objects.filter(
            is_publish=True,
            course__lesson_course__exact=self.kwargs["lesson_course_pk"]
        ).only(
            "title",
            "cover_image",
            "is_last_section",
            "description",
        )
