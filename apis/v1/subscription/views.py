import datetime
import time

from rest_framework import mixins, viewsets, generics, views
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.subscription_app.models import SubscriptionPlan, InstallmentPlan, UserSubscription
from .serializers import (
    SubscriptionSerializer,
    InstallmentPlanSerializer,
    UserSubscriptionSerializer,
    BazarPaySubscriptionSerializer
)
from ...utils.custom_pagination import TwentyPageNumberPagination
from ...utils.custom_response import response


class ListSubscriptionView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(
            is_active=True
        ).select_related(
            "image"
        ).only(
            "name",
            "duration",
            "original_price",
            "discounted_price",
            "image__image",
            "image__height",
            "image__width",
            "has_installment"
        )


class InstallmentPlanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = InstallmentPlanSerializer

    def get_queryset(self):
        return InstallmentPlan.objects.filter(
        is_active=True
        ).defer(
            *self.serializer_class.Meta.exclude,
        )


class UserSubscriptionView(generics.ListAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = TwentyPageNumberPagination

    def get_queryset(self):
        return UserSubscription.objects.filter(is_active=True).select_related("plan").only(
            "plan__name",
            "start_date",
            "end_date",
            "status",
            "transaction_id"
        )


class BazarPaymentView(views.APIView):
    serializer_class = BazarPaySubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = BazarPaySubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # data
        plan_id = serializer.validated_data["plan"].id

        # check user have subscription
        user_subscription = UserSubscription.objects.filter(
            plan_id=plan_id,
            user_id=request.user.id
        ).active_plan().only("id")
        if user_subscription:
            return response(
                status=False,
                message="شما از قبل اشتراک فعال دارید",
                error=True,
                data={},
                status_code=400
            )
        else:
            # create user subscription
            plan = serializer.validated_data["plan"]
            days = plan.duration * 30
            end_data = timezone.now() + datetime.timedelta(days=days)
            UserSubscription.objects.create(
                plan_id=plan_id,
                user_id=request.user.id,
                start_date=timezone.now(),
                end_date=end_data,
                transaction_id=f'bazar_{int(time.time())}'
            )
            return response(
                status=True,
                message="عملیات با موفقیت انجام شد",
                data=serializer.data,
                status_code=201,
                error=False
            )
