from django.db.models import Exists, OuterRef
from rest_framework import viewsets, views
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _

from challenge_app.models import Challenge, ChallengeSubmission
from .filters import ChallengeFilter
from .serializers import ListChallengeSerializer, DetailChallengeSerializer, SubmitChallengeSerializer
from ...utils.custom_pagination import ScrollPagination
from ...utils.custom_response import response


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    filter_class \n
    level --> (easy, easy, medium, hard, expert) \n
    language --> (PY, JA, HTML, C#, JS, C++)
    """
    filterset_class = ChallengeFilter
    pagination_class = ScrollPagination
    permission_classes = (IsAuthenticated,)

    def check_user_submission(self):
        solve_subquery = ChallengeSubmission.objects.filter(
            user_id=self.request.user.id,
            challenge=OuterRef('pk'),
            is_active=True,
            status="accepted"
        ).only("id")
        return solve_subquery

    def get_queryset(self):
        base_query = Challenge.objects.filter(is_active=True, status='published').select_related("image").annotate(
                is_accepted=Exists(self.check_user_submission()),
        )
        base_fields = ("name", "level", "success_percent", "successful_submissions", "points", "coins", "language", "image__image", "image__width", "image__height",)
        detail_field = base_fields + ("description", "answer")
        # test_cases_fields = ("input_data", "expected_output", "order", "challenge_id")
        if self.action == "list":
            base_query = base_query.only(*base_fields)
        elif self.action == "retrieve":
            return base_query.only(*detail_field)
        #     base_query = base_query.prefetch_related(
        #         Prefetch(
        #             "test_cases", queryset=TestCase.objects.filter(is_active=True).only(*test_cases_fields),
        #         )
        #     ).only(*detail_field)
        else:
            raise NotAcceptable()
        return base_query

    def get_serializer_class(self):
        if self.action == 'list':
            return ListChallengeSerializer
        else:
            return DetailChallengeSerializer


class SubmitChallengeView(views.APIView):
    serializer_class = SubmitChallengeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {
            "request": request,
            "challenge_id": kwargs["pk"],
        }
        serializer = self.serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(
            status_code=201,
            status=True,
            error=False,
            message=_("پردازش با موفقت انجام شد"),
            data=serializer.data
        )
