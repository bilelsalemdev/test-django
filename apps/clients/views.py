from django.core.cache import cache
from django.db.models import Prefetch
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from apps.approvals.models import Approval

from .models import Client
from .serializers import ClientCreateSerializer, ClientReadSerializer, ClientResponseSerializer

CLIENT_RESPONSE_EXAMPLE = {
    'data': {
        'id': 'b2c3d4e5-6789-01ab-cdef-234567890abc',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '+1234567890',
        'company': 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
        'created_at': '2025-01-15T11:00:00Z',
    },
    'approval': {
        'id': 'c3d4e5f6-7890-12ab-cdef-345678901bcd',
        'status': 'pending',
        'created_at': '2025-01-15T11:00:00Z',
        'updated_at': '2025-01-15T11:00:00Z',
    },
}


@extend_schema(tags=['Clients'])
class ClientViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return Client.objects.select_related('company').prefetch_related(
            Prefetch(
                'approvals',
                queryset=Approval.objects.only('id', 'status', 'created_at', 'updated_at'),
            )
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        return ClientReadSerializer

    @extend_schema(
        summary='List all clients',
        responses={200: ClientResponseSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Client list',
                value={
                    'count': 1,
                    'next': None,
                    'previous': None,
                    'results': [CLIENT_RESPONSE_EXAMPLE],
                },
                response_only=True,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        cached = cache.get('clients_list')
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set('clients_list', response.data, 60)
        return response

    @extend_schema(
        summary='Create a client',
        request=ClientCreateSerializer,
        responses={201: ClientResponseSerializer},
        examples=[
            OpenApiExample(
                'Create client',
                value={
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com',
                    'phone': '+1234567890',
                    'company': 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
                },
                request_only=True,
            ),
            OpenApiExample(
                'Created response',
                value=CLIENT_RESPONSE_EXAMPLE,
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
            ClientReadSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary='Get client by ID',
        responses={200: ClientResponseSerializer},
        examples=[
            OpenApiExample(
                'Client detail',
                value=CLIENT_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
