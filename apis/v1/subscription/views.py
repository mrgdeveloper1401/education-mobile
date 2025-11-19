from rest_framework import mixins, viewsets, generics
from rest_framework.permissions import IsAuthenticated

from subscription_app.models import SubscriptionPlan
from .serializers import SubscriptionSerializer


class ListSubscriptionView(generics.ListAPIView):
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
        )
