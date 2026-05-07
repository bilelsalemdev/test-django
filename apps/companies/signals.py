from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.approvals.models import Approval

from .models import Company


@receiver(post_save, sender=Company)
def create_company_approval(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            ct = ContentType.objects.get_for_model(Company)
            Approval.objects.create(content_type=ct, object_id=instance.pk)


@receiver(post_save, sender=Company)
def invalidate_company_cache_on_save(sender, instance, **kwargs):
    cache.delete('companies_list')


@receiver(post_delete, sender=Company)
def invalidate_company_cache_on_delete(sender, instance, **kwargs):
    cache.delete('companies_list')
