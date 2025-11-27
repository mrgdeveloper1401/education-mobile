from rest_framework import serializers
from adrf.serializers import ModelSerializer as AdrfModelSerializer, Serializer as AdrfSerializer

from gateway_app.models import Gateway
from subscription_app.models import SubscriptionPlan


class GatewaySerializer(AdrfSerializer):
    description = serializers.CharField(required=False)
    coupon_code = serializers.CharField(required=False)
    plan = serializers.IntegerField()


class ListRetrieveGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway
        fields = '__all__'
