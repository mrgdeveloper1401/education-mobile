from rest_framework import serializers

from apps.subscription_app.models import SubscriptionPlan, InstallmentPlan, UserSubscription


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


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "plan_name",
            "start_date",
            "end_date",
            "status",
            "transaction_id"
        )


class BazarPaySubscriptionSerializer(serializers.Serializer):
    plan = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.filter(is_active=True).only('id'),
    )
