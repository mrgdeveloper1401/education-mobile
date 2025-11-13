from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Question


@receiver(post_save, sender=Question)
async def increasing_display_order(sender, instance, created, **kwargs):
    if created:
        count_question = await Question.objects.filter(exam_id=instance.exam_id).acount()
        await Question.objects.only("display_order").filter(id=instance.id).aupdate(
            display_order=count_question
        )
