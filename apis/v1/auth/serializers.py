from adrf.serializers import Serializer as AdrfSerializer, ModelSerializer as AdrfModelSerializer
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from auth_app.models import User
from core_app.models import Photo
from auth_app.validators import MobileRegexValidator
from subscription_app.models import UserSubscription


class RequestOtpSerializer(AdrfSerializer):
    mobile_phone = serializers.CharField()


class OtpVerifySerializer(AdrfSerializer):
    mobile_phone = serializers.CharField()
    otp = serializers.CharField()


class UserPlanSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "plan_name",
            "time_remaining"
        )

    @extend_schema_field(serializers.DictField())
    def get_time_remaining(self, obj):
        now = timezone.now()
        if obj.end_date <= now:
            return {
                "days": 0,
                "hours": 0,
                "minutes": 0,
                "total_seconds": 0
            }

        remaining = obj.end_date - now
        total_seconds = int(remaining.total_seconds())

        days = remaining.days
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds // 60) % 60
        seconds = total_seconds % 60

        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": total_seconds
        }


class ProfileSerializer(serializers.ModelSerializer):
    ser_image_url = serializers.SerializerMethodField()
    subscriptions = UserPlanSerializer(many=True, read_only=True)
    challenge_total_score = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "image",
            "ser_image_url",
            "bio",
            "subscriptions",
            "challenge_total_score"
        )

    @extend_schema_field(serializers.URLField())
    def get_ser_image_url(self, obj):
        return obj.image.get_image_url if obj.image else None

    @extend_schema_field(serializers.FloatField())
    def get_challenge_total_score(self, obj):
        return obj.score_profile.total_score

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
