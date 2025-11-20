from django_filters.rest_framework import FilterSet

from challenge_app.models import Challenge


class ChallengeFilter(FilterSet):
    class Meta:
        model = Challenge
        fields = {
            "level": ("iexact",),
            "language": ("iexact",),
        }
