from django.core.management import BaseCommand
from django.db import transaction

from auth_app.models import User
from challenge_app.models import UserChallengeScore


class Command(BaseCommand):
    help = 'Creates field user score'

    def handle(self, *args, **options):
        users_without_score = User.objects.filter(score_profile__isnull=True)

        count = users_without_score.count()

        if count > 0:
            with transaction.atomic():
                user_scores = [
                    UserChallengeScore(user_id=user.id)
                    for user in users_without_score
                ]
                UserChallengeScore.objects.bulk_create(user_scores)
            self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {count} user_score records')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('All users already have user_score records')
            )
