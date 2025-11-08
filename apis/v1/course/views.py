from django.db.models import Prefetch, Exists, OuterRef
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, permissions, generics
from rest_framework.exceptions import NotFound

from . import serializers
from course_app.models import Category, LessonCourse, Section, StudentAccessSection, SectionVideo, SectionFile
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
        ).order_by("-id")


class SectionLessonCourseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.SectionLessonCourseSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='lesson_course_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID of the lesson course'
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='lesson_course_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID of the lesson course'
            ),
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description='ID of the section'
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        base_query = Section.objects.filter(
            is_publish=True,
            course__lesson_course__exact=self.kwargs["lesson_course_pk"]
        )
        if self.action == "list":
            return base_query.only(
                "title",
                "cover_image",
                "is_last_section",
                "description",
            ).annotate(
                has_access=Exists(
                    StudentAccessSection.objects.filter(
                        section_id=OuterRef("id"),
                        student__user_id=self.request.user.id,
                        is_access=True
                    )
                )
            ).prefetch_related(
                Prefetch(
                    "student_section",
                    queryset=StudentAccessSection.objects.only("section_id", "is_access")
                )
            )
        elif self.action == "retrieve":
            return base_query.prefetch_related(
                Prefetch(
                    "section_videos", SectionVideo.objects.filter(
                        is_publish=True
                    ).only(
                        "section_id", "video", "title", "video_url"
                    ),
                ),
                Prefetch(
                    "section_files", SectionFile.objects.filter(
                        is_publish=True
                    ).only(
                        "section_id", "title", "zip_file", "file_type"
                    )
                )
            ).only(
                "title",
                "cover_image",
                "is_last_section",
                "description",
            )
        else:
            raise NotFound()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.DetailSectionLessonCourseSerializer
        return super().get_serializer_class()
