from django.core.cache import cache
from django.db.models import Prefetch
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.approvals.models import Approval

from .models import Company
from .serializers import CompanyCreateSerializer, CompanyReadSerializer, CompanyResponseSerializer

COMPANY_RESPONSE_EXAMPLE = {
    'data': {
        'id': 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
        'name': 'TechStart',
        'type': 'startup',
        'employee_count': None,
        'industry': None,
        'funding_stage': 'Series A',
        'founded_year': 2022,
        'revenue': None,
        'stock_symbol': None,
        'created_at': '2025-01-15T10:30:00Z',
    },
    'approval': {
        'id': 'f1e2d3c4-5678-90ab-cdef-1234567890ab',
        'status': 'pending',
        'created_at': '2025-01-15T10:30:00Z',
        'updated_at': '2025-01-15T10:30:00Z',
    },
}


@extend_schema(tags=['Companies'])
class CompanyViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return Company.objects.prefetch_related(
            Prefetch(
                'approvals',
                queryset=Approval.objects.only('id', 'status', 'created_at', 'updated_at'),
            )
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return CompanyCreateSerializer
        return CompanyReadSerializer

    @extend_schema(
        summary='List all companies',
        responses={200: CompanyResponseSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Company list',
                value={
                    'count': 1,
                    'next': None,
                    'previous': None,
                    'results': [COMPANY_RESPONSE_EXAMPLE],
                },
                response_only=True,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        if not self.get_queryset().exists():
            raise ValidationError({'detail': 'No companies found.'})
        cached = cache.get('companies_list')
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set('companies_list', response.data, 60)
        return response

    @extend_schema(
        summary='Create a company',
        request=CompanyCreateSerializer,
        responses={201: CompanyResponseSerializer},
        examples=[
            OpenApiExample(
                'Create small business',
                value={
                    'name': 'Local Shop',
                    'type': 'small_business',
                    'employee_count': 15,
                    'industry': 'Retail',
                },
                request_only=True,
            ),
            OpenApiExample(
                'Create startup',
                value={
                    'name': 'TechStart',
                    'type': 'startup',
                    'funding_stage': 'Series A',
                    'founded_year': 2022,
                },
                request_only=True,
            ),
            OpenApiExample(
                'Create corporate',
                value={
                    'name': 'MegaCorp',
                    'type': 'corporate',
                    'revenue': '5000000.00',
                    'stock_symbol': 'MEGA',
                },
                request_only=True,
            ),
            OpenApiExample(
                'Created response',
                value=COMPANY_RESPONSE_EXAMPLE,
                response_only=True,
                status_codes=['201'],
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance = self.get_queryset().get(pk=instance.pk)
        return Response(
            CompanyReadSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary='Get company by ID',
        responses={200: CompanyResponseSerializer},
        examples=[
            OpenApiExample(
                'Company detail',
                value=COMPANY_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
