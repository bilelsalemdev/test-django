from rest_framework import serializers

from .models import Approval


class ApprovalInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = ['id', 'status', 'created_at', 'updated_at']


class ApprovalReadSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = Approval
        fields = ['id', 'status', 'content_type', 'object_id', 'reviewed_by', 'created_at', 'updated_at']

    @staticmethod
    def get_content_type(obj):
        return obj.content_type.model


class ApprovalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = ['status']

    def update(self, instance, validated_data):
        validated_data['reviewed_by'] = self.context['request'].user
        return super().update(instance, validated_data)
