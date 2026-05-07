from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.approvals.models import Approval

from .models import Client


@receiver(post_save, sender=Client)
def create_client_approval(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            ct = ContentType.objects.get_for_model(Client)
            Approval.objects.create(content_type=ct, object_id=instance.pk)


@receiver(post_save, sender=Client)
def invalidate_client_cache_on_save(sender, instance, **kwargs):
    cache.delete('clients_list')


@receiver(post_delete, sender=Client)
def invalidate_client_cache_on_delete(sender, instance, **kwargs):
    cache.delete('clients_list')
