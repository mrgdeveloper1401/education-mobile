from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import serializers

from challenge_app.models import Challenge


class ListChallengeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = (
            "id",
            "name",
            "language",
            "level",
            "success_percent",
            "points",
            "coins",
            "image_url",
        )

    @extend_schema_field(serializers.URLField())
    def get_image_url(self, obj):
        return obj.image.course_image


class DetailChallengeSerializer(ListChallengeSerializer):
    class Meta(ListChallengeSerializer.Meta):
        fields = ListChallengeSerializer.Meta.fields + (
            "description",
            "time_limit",
            "memory_limit",
            "total_submissions",
            "successful_submissions",
            "avg_completion_time",
        )
