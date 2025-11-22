from rest_framework import mixins, viewsets, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from subscription_app.models import SubscriptionPlan, InstallmentPlan, UserSubscription
from .serializers import SubscriptionSerializer, InstallmentPlanSerializer, UserSubscriptionSerializer
from ...utils.custom_pagination import TwentyPageNumberPagination


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
