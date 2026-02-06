from django.db.models import Exists, OuterRef
from django_filters.rest_framework import FilterSet, BooleanFilter

from apps.challenge_app.models import Challenge, ChallengeSubmission


class ChallengeFilter(FilterSet):
    is_accepted = BooleanFilter(method='filter_is_accepted')

    class Meta:
        model = Challenge
        fields = {
            "level": ("iexact",),
            "language": ("iexact",)
        }

    def filter_is_accepted(self, queryset, name, value):
        solve_subquery = ChallengeSubmission.objects.filter(
            user_id=self.request.user.id,
            challenge=OuterRef('pk'),
            is_active=True,
            status="accepted"
        )

        if value:
            return queryset.filter(Exists(solve_subquery))
        else:
            return queryset.filter(~Exists(solve_subquery))