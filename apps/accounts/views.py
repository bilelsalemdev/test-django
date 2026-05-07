from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    CustomTokenObtainPairSerializer,
    LoginResponseSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    TokenRefreshResponseSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Register a new user',
        request=RegisterSerializer,
        responses={201: RegisterResponseSerializer},
        examples=[
            OpenApiExample(
                'Register regular user',
                value={'email': 'user@example.com', 'password': 'securepass123'},
                request_only=True,
            ),
            OpenApiExample(
                'Register admin user',
                value={'email': 'admin@example.com', 'password': 'securepass123', 'role': 'admin'},
                request_only=True,
            ),
            OpenApiExample(
                'Success response',
                value={'email': 'user@example.com', 'role': 'user'},
                response_only=True,
                status_codes=['201'],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'email': user.email, 'role': user.role},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        tags=['Auth'],
        summary='Login and get JWT tokens',
        request=CustomTokenObtainPairSerializer,
        responses={200: LoginResponseSerializer},
        examples=[
            OpenApiExample(
                'Login request',
                value={'email': 'user@example.com', 'password': 'securepass123'},
                request_only=True,
            ),
            OpenApiExample(
                'Login response',
                value={
                    'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'user': {'email': 'user@example.com', 'role': 'user'},
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):
    @extend_schema(
        tags=['Auth'],
        summary='Refresh access token',
        request=TokenRefreshSerializer,
        responses={200: TokenRefreshResponseSerializer},
        examples=[
            OpenApiExample(
                'Refresh request',
                value={'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'},
                request_only=True,
            ),
            OpenApiExample(
                'Refresh response',
                value={'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'},
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
