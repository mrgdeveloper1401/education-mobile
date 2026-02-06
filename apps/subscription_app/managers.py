from django.utils import timezone

from django.db import models


class SubQuerySet(models.QuerySet):
    def active_plan(self):
        return self.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
            status='active',
        )


class SubManager(models.Manager):
    def get_queryset(self):
        return SubQuerySet(self.model, using=self._db)
