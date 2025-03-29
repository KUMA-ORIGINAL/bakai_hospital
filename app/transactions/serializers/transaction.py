from rest_framework import serializers

from organizations.models import Organization
from ..models import Transaction, TransactionService
from .transaction_service import TransactionServiceSerializer
from ..services import generate_payment_link


class TransactionCreateSerializer(serializers.ModelSerializer):
    services = TransactionServiceSerializer(many=True, write_only=True)
    payment_url = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'patient',
            'staff',
            'services',
            'payment_url'
        ]
        extra_kwargs = {
            'patient': {'write_only': True},
            'staff': {'write_only': True},
        }

    def create(self, validated_data):
        services_data = validated_data.pop('services')

        service_instances = [item['service'] for item in services_data]
        total_price = sum(service.price for service in service_instances)
        validated_data['total_price'] = 1

        organization = Organization.objects.filter(name='Национальный Госпиталь').first()
        validated_data['organization_id'] = organization.pk
        validated_data['status'] = 'paid'

        transaction = Transaction.objects.create(**validated_data)
        for service_data in services_data:
            TransactionService.objects.create(transaction=transaction, **service_data)
        return transaction

    def get_payment_url(self, obj):
        return generate_payment_link(obj)


class TransactionDetailSerializer(serializers.ModelSerializer):
    services = TransactionServiceSerializer(many=True, read_only=True)
    inn = serializers.CharField(source='patient.inn', read_only=True)
    staff_full_name = serializers.CharField(source='staff.full_name', read_only=True)
    patient_full_name = serializers.CharField(source='patient.full_name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'staff_full_name',
            'patient_full_name',
            'total_price',
            'inn',
            'status',
            'created_at',
            'services',
        ]
