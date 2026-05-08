import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.PROTECT,
        related_name='clients',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    approvals = GenericRelation('approvals.Approval')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
