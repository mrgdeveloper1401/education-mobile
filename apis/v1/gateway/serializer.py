from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from adrf.serializers import Serializer as AdrfSerializer

from gateway_app.models import Gateway, ResultGateway


class GatewaySerializer(AdrfSerializer):
    description = serializers.CharField(required=False)
    coupon_code = serializers.CharField(required=False)
    plan = serializers.IntegerField()
    gateway_name = serializers.CharField()


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


class ListRetrieveResultGateWaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultGateway
        fields = (
            "id",
            "created_at",
            "paid_at",
            "amount",
            "result",
            "status",
            "ref_number",
            "card_number",
            "order_id",
            "message"
        )
