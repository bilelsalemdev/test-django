import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class Company(models.Model):
    TYPE_CHOICES = [
        ('small_business', 'Small Business'),
        ('startup', 'Startup'),
        ('corporate', 'Corporate'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)

    employee_count = models.IntegerField(null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)

    funding_stage = models.CharField(max_length=100, null=True, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)

    revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    stock_symbol = models.CharField(max_length=10, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    approvals = GenericRelation('approvals.Approval')

    class Meta:
        verbose_name_plural = 'companies'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
