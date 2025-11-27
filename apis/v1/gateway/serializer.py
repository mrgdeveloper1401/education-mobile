from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from adrf.serializers import ModelSerializer as AdrfModelSerializer, Serializer as AdrfSerializer

from gateway_app.models import Gateway
from subscription_app.models import SubscriptionPlan


class GatewaySerializer(AdrfSerializer):
    description = serializers.CharField(required=False)
    coupon_code = serializers.CharField(required=False)
    plan = serializers.IntegerField()


class ListRetrieveGatewaySerializer(serializers.ModelSerializer):
    plan_name = serializers.SerializerMethodField()

    class Meta:
        model = Gateway
        fields = (
            "id",
            "subscription",
            "plan_name",
            "is_complete",
            "updated_at",
            "created_at"
        )

    @extend_schema_field(serializers.CharField())
    def get_plan_name(self, obj):
        return obj.subscription.name
