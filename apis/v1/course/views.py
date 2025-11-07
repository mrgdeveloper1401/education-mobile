from rest_framework import mixins, viewsets, permissions, generics

from . import serializers
from course_app.models import Category, LessonCourse, Section
from ...utils.custom_pagination import TwentyPageNumberPagination


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
        ).select_related("course__category").only(
            "course__category__category_name",
            "course__course_name",
            "course__project_counter",
            "course__course_image",
            "for_mobile",
            "class_name",
            "progress"
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
