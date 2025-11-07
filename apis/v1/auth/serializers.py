from adrf.serializers import Serializer
from rest_framework import serializers

from auth_app.models import User


class RequestOtpSerializer(Serializer):
    mobile_phone = serializers.CharField()


class OtpVerifySerializer(Serializer):
    mobile_phone = serializers.CharField()
    otp = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "image",
            "bio"
        )
