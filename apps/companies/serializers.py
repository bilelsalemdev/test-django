from rest_framework import serializers

from apps.approvals.serializers import ApprovalInlineSerializer

from .models import Company

SMALL_BUSINESS_FIELDS = {'employee_count', 'industry'}
STARTUP_FIELDS = {'funding_stage', 'founded_year'}
CORPORATE_FIELDS = {'revenue', 'stock_symbol'}

TYPE_FIELDS = {
    'small_business': SMALL_BUSINESS_FIELDS,
    'startup': STARTUP_FIELDS,
    'corporate': CORPORATE_FIELDS,
}


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'type',
            'employee_count', 'industry',
            'funding_stage', 'founded_year',
            'revenue', 'stock_symbol',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        company_type = data.get('type')
        required = TYPE_FIELDS.get(company_type, set())

        for field in required:
            if data.get(field) is None:
                raise serializers.ValidationError(
                    {field: f'Required for {company_type}.'}
                )

        all_type_fields = SMALL_BUSINESS_FIELDS | STARTUP_FIELDS | CORPORATE_FIELDS
        for field in all_type_fields - required:
            data.pop(field, None)

        return data


class CompanyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'type',
            'employee_count', 'industry',
            'funding_stage', 'founded_year',
            'revenue', 'stock_symbol',
            'created_at',
        ]


class CompanyResponseSerializer(serializers.Serializer):
    data = CompanyDataSerializer()
    approval = ApprovalInlineSerializer()


class CompanyReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'type',
            'employee_count', 'industry',
            'funding_stage', 'founded_year',
            'revenue', 'stock_symbol',
            'created_at',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        approval = instance.approvals.first()
        return {
            'data': data,
            'approval': ApprovalInlineSerializer(approval).data if approval else None,
        }
