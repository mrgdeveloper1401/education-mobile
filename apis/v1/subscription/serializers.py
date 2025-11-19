from rest_framework import serializers

from subscription_app.models import SubscriptionPlan


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
            "image"
        )
