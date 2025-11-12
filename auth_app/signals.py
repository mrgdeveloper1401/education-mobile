from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from .models import User, Coach, Student


@receiver(post_save, sender=User)
async def create_profile(sender, instance, created, **kwargs):
    if created and instance.is_coach:
        await Coach.objects.acreate(user=instance)
    else:
        await Student.objects.acreate(user=instance)


@receiver(post_save, sender=Student)
async def create_student_referral_number(sender, instance, created, **kwargs):
    if created:
        year = timezone.now().year
        referral_code = f'std{year}{instance.id}'
        await Student.objects.only("id", "referral_code").filter(
            id=instance.id,
        ).aupdate(
            referral_code=referral_code
        )


@receiver(post_save, sender=Coach)
async def create_coach_coach_number(sender, instance, created, **kwargs):
    if created:
        year = timezone.now().year
        coach_number = f"coach{year}{instance.id}"
        await Coach.objects.only("id", "coach_number").filter(
            id=instance.id
        ).aupdate(
            coach_number=coach_number
        )
