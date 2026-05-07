from rest_framework import serializers

from apps.approvals.serializers import ApprovalInlineSerializer

from .models import Client


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'company']
        read_only_fields = ['id']


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
