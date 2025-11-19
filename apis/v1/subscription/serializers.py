from rest_framework import serializers

from subscription_app.models import SubscriptionPlan, InstallmentPlan


class SubscriptionSerializer(serializers.ModelSerializer):
    image = serializers.URLField(source="image.course_image", read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = (
            "id",
            "name",
            "duration",
            "original_price",
            "discounted_price",
            "image",
            "has_installment"
        )


class InstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPlan
        exclude = (
            "is_active",
            "created_at",
            "updated_at",
        )
