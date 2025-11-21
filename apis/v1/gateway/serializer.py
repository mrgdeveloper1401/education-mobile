from rest_framework import serializers
from adrf.serializers import ModelSerializer as AdrfModelSerializer

from gateway_app.models import Gateway


class GatewaySerializer(AdrfModelSerializer):
    description = serializers.CharField(required=False)
    coupon_code = serializers.CharField(required=False)

    class Meta:
        model = Gateway
        fields = (
            "description",
            "subscription",
            "coupon_code"
        )
