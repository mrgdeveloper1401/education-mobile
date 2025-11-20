from rest_framework import serializers

from challenge_app.models import Challenge


class ChallengeSerializer(serializers.ModelSerializer):
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
        )