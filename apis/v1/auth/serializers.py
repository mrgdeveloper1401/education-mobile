from adrf.serializers import Serializer as AdrfSerializer, ModelSerializer as AdrfModelSerializer
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from auth_app.models import User
from core_app.models import Photo
from auth_app.validators import MobileRegexValidator


class RequestOtpSerializer(AdrfSerializer):
    mobile_phone = serializers.CharField()


class OtpVerifySerializer(AdrfSerializer):
    mobile_phone = serializers.CharField()
    otp = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    ser_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "image",
            "ser_image_url",
            "bio",
        )

    @extend_schema_field(serializers.URLField())
    def get_ser_image_url(self, obj):
        return obj.image.get_image_url if obj.image else None

    def validate_image(self, data):
        user_id = self.context['request'].user.id
        image = Photo.objects.filter(
            id=data.id,
            upload_by_id=user_id,
            is_active=True,
        ).only("id")
        if not image.exists():
            raise NotFound()
        else:
            return data


class UploadImageSerializer(AdrfModelSerializer):
    class Meta:
        model = Photo
        fields = (
            "id",
            "image"
        )


class LogInByPhoneSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=(MobileRegexValidator(),),)
    password = serializers.CharField()
