import os

from django.db import transaction
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Recipe


@receiver(post_delete, sender=Recipe)
def delete_image(sender, instance, *args, **kwargs):
    instance.image.delete(save=False)


@receiver(pre_save, sender=Recipe)
def delete_old_image(sender, instance, *args, **kwargs):
    if instance.pk is None:
        pass

    try:
        old_image = Recipe.objects.get(pk=instance.pk).image
    except Recipe.DoesNotExist:
        old_image = None

    new_image = instance.image
    if old_image is not None and old_image != new_image:
        if os.path.isfile(path := old_image.path):
            transaction.on_commit(lambda: os.remove(path))
