from django.db.models import Prefetch, Exists, OuterRef
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import mixins, viewsets, permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core_app.models import Attachment
from exam_app.models import SectionExam, Question, Choice, StudentExamAttempt, StudentAnswer
from course_app.models import Category, LessonCourse, Section, StudentAccessSection, SectionVideo, CategoryComment, \
    CommentAttachment
from .filters import StudentExamAttemptFilter
from .serializers import (
    CreateStudentExamAttemptSerializer,
    ListDetailStudentExamAttemptSerializer,
    StudentAnswerSerializer,
    CategoryCommentSerializer,
    ListDetailCategoryCommentSerializer,
    UpdateCategoryCommentSerializer,
    UploadAttachmentSerializer,
    ListCategorySerializer,
    ListClassSerializer,
    ExamQuestionSerializer,
    SectionLessonCourseSerializer,
    DetailSectionLessonCourseSerializer
)
from ...utils.custom_pagination import TwentyPageNumberPagination, ScrollPagination
from ...utils.custom_permissions import IsOwnerOrReadOnly
from ...utils.custom_response import response


class ListDetailCategoryView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ListCategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Category.objects.filter(
        is_active=True
    ).only(
        "category_name",
    )


class ListLessonClassView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ListClassSerializer
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
    serializer_class = SectionLessonCourseSerializer
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

    def get_object(self):
        obj = super().get_object()

        if not obj.has_access:
            raise PermissionDenied("شما به این بخش دسترسی ندارید")

        return obj

    def get_queryset(self):
        # if getattr(self, 'swagger_fake_view', False):
        #     return Question.objects.none()

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
                Prefetch(
                    "section_exams", SectionExam.objects.filter(is_active=True).only(
                        "title",
                        "description",
                        'exam_type',
                        "total_score",
                        "passing_score",
                        # "time_limit",
                        "section_id"
                    ),
                )
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
            return DetailSectionLessonCourseSerializer
        return super().get_serializer_class()


class QuestionView(ListAPIView):
    serializer_class = ExamQuestionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.request.user.id
        exam_id = self.kwargs["exam_pk"]

        # Cache the result to avoid duplicate queries
        if not hasattr(self, '_has_active_attempt'):
            self._has_active_attempt = StudentExamAttempt.objects.filter(
                student__user_id=user_id,
                exam_id=exam_id,
                submitted_at__isnull=True,
                status='in_progress'
            ).exists()

        if not self._has_active_attempt:
            raise PermissionDenied(detail="شما در آزمون شرکت نکرده اید")

        return Question.objects.filter(
            is_active=True,
            exam_id=exam_id,
        ).only(
            "question_text", "question_type", "score",
            "display_order", "explanation"
        ).prefetch_related(
            Prefetch(
                "choices",
                queryset=Choice.objects.filter(is_active=True).only(
                    "question_id", "choice_text"
                ),
            )
        )

class StudentExamAttemptView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    شروع ازمون \n
    filter query --> (in_progress, done) \n
    filter query, is_passed --> bool (true, false) \n
    pagination --> 20 item
    """
    serializer_class = ListDetailStudentExamAttemptSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = StudentExamAttemptFilter
    pagination_class = TwentyPageNumberPagination

    def get_queryset(self):
        fields = ('exam__passing_score', "started_at", "total_score", "submitted_at", "obtained_score", "is_passed", "status")
        return StudentExamAttempt.objects.filter(
            student__user_id=self.request.user.id,
        ).select_related("exam").only(*fields).order_by("-id")

    def get_serializer_class(self):
        if self.action == "create":
            return CreateStudentExamAttemptSerializer
        else:
            return super().get_serializer_class()


class StudentAnswerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = StudentAnswerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # if getattr(self, 'swagger_fake_view', False):
        #     return Question.objects.none()

        return StudentAnswer.objects.filter(
            student__user_id=self.request.user.id,
            question_id=self.kwargs["pk"],
            is_active=True,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['exam_pk'] = self.kwargs["exam_pk"]
        context['question_pk'] = self.kwargs["pk"]
        return context


common_params = [
    OpenApiParameter(
        name='id',
        type=int,
        location=OpenApiParameter.PATH,
        description='ID of the category_comment'
    ),
    OpenApiParameter(
        name="category_pk",
        type=int,
        location=OpenApiParameter.PATH,
        description='category_pk of the category_comment'
    )
]
list_params = [
    OpenApiParameter(
        name='category_pk',
        type=int,
        location=OpenApiParameter.PATH,
        description='category_pk of the category_comment'
    )
]
@extend_schema_view(
    retrieve=extend_schema(parameters=common_params),
    update=extend_schema(parameters=common_params),
    partial_update=extend_schema(parameters=common_params),
    destroy=extend_schema(parameters=common_params),
    list=extend_schema(parameters=list_params),
    create=extend_schema(parameters=list_params),
)
class CategoryCommentViewSet(viewsets.ModelViewSet):
    """
    pagination --> 20 item \n
    scroll pagination --> (page_size = 20 max_page_size = 100 page_size_query_param = 'page_size')

    """
    pagination_class = ScrollPagination
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "create":
            return CategoryCommentSerializer
        if self.action == "update":
            return UpdateCategoryCommentSerializer
        else:
            return ListDetailCategoryCommentSerializer

    def get_queryset(self):
        # if getattr(self, 'swagger_fake_view', False):
        #     return Question.objects.none()

        return CategoryComment.objects.filter(
            is_active=True,
            category_id=self.kwargs["category_pk"],
        ).select_related("user").order_by("-id").only(
            "user__first_name",
            "user__last_name",
            "comment_body",
            "is_pined",
            "level",
            "lft",
            "tree_id",
            "parent_id",
            "rght",
            "created_at",
            "updated_at",
        ).prefetch_related(
            Prefetch(
                "attachments", CommentAttachment.objects.filter(
                    is_active=True
                ).select_related("file").only("file__file", "comment_id", 'file__file_type')
            )
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['category_pk'] = self.kwargs["category_pk"]
        return context

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class UploadAttachmentView(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UploadAttachmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Attachment.objects.filter(upload_by_id=self.request.user.id).only("file")


class ExamDoneView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        exam_id = kwargs["exam_pk"]
        exam_last = StudentExamAttempt.objects.filter(
            exam_id=exam_id,
            is_active=True,
            student__user_id=request.user.id,
            submitted_at__isnull=True,
            status="in_progress"
        ).only("id").last()
        if not exam_last:
            raise PermissionDenied("شما ازمون فعالی رو ندارید")
        else:
            exam_last.status = "done"
            exam_last.submitted_at = timezone.now()
            exam_last.save()
            return response(
                error=False,
                status_code=200,
                data={"exam_last_id": exam_last.id},
                message="پردازش با موفقیت انجام شد",
                status=True
            )
