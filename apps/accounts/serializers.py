import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'role']

    def validate_first_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('First name is required.')
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', value):
            raise serializers.ValidationError('First name contains invalid characters.')
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Last name is required.')
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', value):
            raise serializers.ValidationError('Last name contains invalid characters.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        return value.lower()

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RegisterResponseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.ChoiceField(choices=['admin', 'user'])


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
        }
        return data


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
