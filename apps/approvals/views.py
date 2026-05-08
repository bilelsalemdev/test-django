from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Approval
from .permissions import IsAdminUser
from .serializers import ApprovalReadSerializer, ApprovalUpdateSerializer

@extend_schema(tags=['Approvals'])
class ApprovalViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return Approval.objects.select_related('content_type', 'reviewed_by')

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return ApprovalUpdateSerializer
        return ApprovalReadSerializer

    @extend_schema(
        summary='List all approvals (admin only)',
        responses={200: ApprovalReadSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Approval list',
                value={
                    'count': 2,
                    'next': None,
                    'previous': None,
                    'results': [
                        {
                            'id': 'f1e2d3c4-5678-90ab-cdef-1234567890ab',
                            'status': 'pending',
                            'content_type': 'company',
                            'object_id': 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
                            'reviewed_by': None,
                            'created_at': '2025-01-15T10:30:00Z',
                            'updated_at': '2025-01-15T10:30:00Z',
                        },
                        {
                            'id': 'c3d4e5f6-7890-12ab-cdef-345678901bcd',
                            'status': 'approved',
                            'content_type': 'client',
                            'object_id': 'b2c3d4e5-6789-01ab-cdef-234567890abc',
                            'reviewed_by': 1,
                            'created_at': '2025-01-15T11:00:00Z',
                            'updated_at': '2025-01-15T11:05:00Z',
                        },
                    ],
                },
                response_only=True,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Update approval status (admin only)',
        request=ApprovalUpdateSerializer,
        responses={200: ApprovalReadSerializer},
        examples=[
            OpenApiExample(
                'Approve',
                value={'status': 'approved'},
                request_only=True,
            ),
            OpenApiExample(
                'Reject',
                value={'status': 'rejected'},
                request_only=True,
            ),
            OpenApiExample(
                'Approved response',
                value={
                    'id': 'f1e2d3c4-5678-90ab-cdef-1234567890ab',
                    'status': 'approved',
                    'content_type': 'company',
                    'object_id': 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
                    'reviewed_by': 1,
                    'created_at': '2025-01-15T10:30:00Z',
                    'updated_at': '2025-01-15T12:00:00Z',
                },
                response_only=True,
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
