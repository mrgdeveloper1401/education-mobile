from django.db.models import Prefetch, Exists, OuterRef
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, permissions, generics
from rest_framework.exceptions import NotFound
from adrf.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from adrf.viewsets import GenericViewSet as AdrfGenericViewSet
from adrf.generics import ListAPIView as AdrfListAPIView

from exam_app.models import SectionExam, Question, Choice, StudentExamAttempt
from . import serializers
from course_app.models import Category, LessonCourse, Section, StudentAccessSection, SectionVideo
from .serializers import StudentExamAttemptSerializer
from ...utils.custom_pagination import TwentyPageNumberPagination
from ...utils.custom_permissions import AsyncIsAuthenticated


class ListCategoryView(generics.ListAPIView):
    serializer_class = serializers.ListCategorySerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Category.objects.filter(
        is_active=True
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
        ).select_related("course__category", "course__course_image").only(
            "course__category__category_name",
            "course__course_name",
            "course__project_counter",
            "course__course_image__image",
            "course__course_image__height",
            "course__course_image__width",
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
            is_active=True,
            course__lesson_course__exact=self.kwargs["lesson_course_pk"]
        ).select_related("cover_image").annotate(
                has_access=Exists(
                    StudentAccessSection.objects.filter(
                        section_id=OuterRef("id"),
                        student__user_id=self.request.user.id,
                        is_access=True
                    )
                )
            )
        if self.action == "list":
            return base_query.only(
                "title",
                "cover_image",
                "is_last_section",
                "description",
                "cover_image__image",
                "cover_image__height",
                "cover_image__width",
            )
        elif self.action == "retrieve":
            return base_query.prefetch_related(
                Prefetch(
                    "section_videos", SectionVideo.objects.filter(
                        is_active=True
                    ).select_related("video").only(
                        "section_id", "video__video_file", "title"
                    ),
                ),
            ).only(
                "title",
                "cover_image__image",
                "cover_image__height",
                "cover_image__width",
                "is_last_section",
                "description",
            )
        else:
            raise NotFound()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.DetailSectionLessonCourseSerializer
        return super().get_serializer_class()


class SectionExamViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    AdrfGenericViewSet
):
    serializer_class = serializers.SectionExamSerializer
    permission_classes = (AsyncIsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='sections_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID of the section_pk'
            ),
            OpenApiParameter(
                name='lesson_course_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID of the lesson course'
            ),
        ]
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='sections_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID of the section_pk'
            ),
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description='ID of the section'
            ),
            OpenApiParameter(
                name='lesson_course_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID of the lesson course'
            ),
        ]
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    def get_queryset(self):
        return SectionExam.objects.filter(
            section_id=self.kwargs["sections_pk"],
            is_active=True,
        ).only(
            "title",
            "description",
            "exam_type",
            "total_score",
            "passing_score",
            "time_limit"
        )



class QuestionView(AdrfListAPIView):
    serializer_class = serializers.ExamQuestionSerializer
    permission_classes = (AsyncIsAuthenticated,)

    def get_queryset(self):
        return Question.objects.filter(
            is_active=True,
            exam_id=self.kwargs["exam_pk"],
        ).only(
            "question_text",
            "question_type",
            "score",
            "display_order"
        ).prefetch_related(
            Prefetch(
                "choices",
                queryset=Choice.objects.filter(is_active=True).only("question_id", "choice_text"),
            )
        )


class ListCreateStudentExamAttemptView(
    ListModelMixin,
    CreateModelMixin,
    AdrfGenericViewSet
):
    serializer_class = StudentExamAttemptSerializer
    permission_classes = (AsyncIsAuthenticated,)

    def get_queryset(self):
        return StudentExamAttempt.objects.filter(
            student__user_id=self.request.user.id,
        )
