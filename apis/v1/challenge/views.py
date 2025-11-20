from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.exceptions import NotAcceptable

from challenge_app.models import Challenge, TestCase
from .filters import ChallengeFilter
from .serializers import ListChallengeSerializer, DetailChallengeSerializer


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    filter_class \n
    level --> (easy, easy, medium, hard, expert) \n
    language --> (PY, JA, HTML, C#, JS, C++)
    """
    filterset_class = ChallengeFilter
    @extend_schema(
        parameters=(
            OpenApiParameter(
            name="challenge_id",
            type=int,
            description="Challenge ID",
            location=OpenApiParameter.PATH,
        ),
        ),
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        base_query = Challenge.objects.filter(is_active=True).select_related("image")
        base_fields = ("name", "level", "success_percent", "points", "coins", "language", "image__image", "image__width", "image__height",)
        detail_field = base_fields + ("description", "time_limit", "memory_limit", "total_submissions", "total_submissions", "avg_completion_time", "successful_submissions")
        test_cases_fields = ("input_data", "expected_output", "order", "challenge_id")
        if self.action == "list":
            base_query = base_query.only(*base_fields)
        elif self.action == "retrieve":
            base_query = base_query.prefetch_related(
                Prefetch(
                    "test_cases", queryset=TestCase.objects.filter(is_active=True).only(*test_cases_fields),
                )
            ).only(*detail_field)
        else:
            raise NotAcceptable()
        return base_query

    def get_serializer_class(self):
        if self.action == 'list':
            return ListChallengeSerializer
        else:
            return DetailChallengeSerializer
