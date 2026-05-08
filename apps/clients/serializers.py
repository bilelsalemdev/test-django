import re

from rest_framework import serializers

from apps.approvals.serializers import ApprovalInlineSerializer

from .models import Client

class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'company']
        read_only_fields = ['id']

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

    def validate_email(self, value):
        return value.lower()

    def validate_phone(self, value):
        if value:
            value = value.strip()
            if not re.match(r'^\+?[0-9\s\-()]{7,20}$', value):
                raise serializers.ValidationError('Enter a valid phone number.')
        return value

class ClientDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'company', 'created_at']

class ClientResponseSerializer(serializers.Serializer):
    data = ClientDataSerializer()
    approval = ApprovalInlineSerializer()

class ClientReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'company', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        approval = instance.approvals.first()
        return {
            'data': data,
            'approval': ApprovalInlineSerializer(approval).data if approval else None,
        }
