from django.db import transaction
from rest_framework import serializers

from organizations.models import Organization
from services.models import Service
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
            'phone_number',
            'payment_url'
        ]
        extra_kwargs = {
            'patient': {'write_only': True},
            'staff': {'write_only': True},
            'phone_number': {'write_only': True},
        }

    def create(self, validated_data):
        services_data = validated_data.pop('services')

        # ОПТИМИЗАЦИЯ 1: Получаем все нужные service ID сразу
        service_ids = [item['service'].id for item in services_data]

        # ОПТИМИЗАЦИЯ 2: Одним запросом получаем все services с их категориями и payout_account
        services_dict = {
            service.id: service
            for service in Service.objects.select_related('payout_account')
            .filter(id__in=service_ids)
        }

        # ОПТИМИЗАЦИЯ 3: Получаем организацию один раз, можно закешировать
        organization = Organization.objects.filter(name='Национальный Госпиталь').first()
        if not organization:
            raise serializers.ValidationError("Организация не найдена.")

        # Проверяем payout_accounts
        payout_accounts = {
            services_dict[service_id].payout_account_id
            for service_id in service_ids
            if services_dict[service_id].payout_account_id
        }

        if len(payout_accounts) > 1:
            raise serializers.ValidationError("Все услуги должны иметь один и тот же счёт для выплат.")

        # Рассчитываем общую стоимость и подготавливаем данные для TransactionService
        total_price = 0
        transaction_services_data = []

        for item in services_data:
            service_id = item['service'].id
            service = services_dict[service_id]  # Берем из уже загруженного словаря
            quantity = item.get('quantity', 1)
            total_price += service.price * quantity

            transaction_service_data = {
                'service': service,
                'quantity': quantity,
                'service_price': service.price,
                'service_provided': item.get('service_provided', False),
                'service_note': item.get('service_note', ''),
            }
            transaction_services_data.append(transaction_service_data)

        validated_data['total_price'] = total_price
        validated_data['organization'] = organization

        with transaction.atomic():
            transaction_obj = Transaction.objects.create(**validated_data)

            transaction_services = [
                TransactionService(transaction=transaction_obj, **data)
                for data in transaction_services_data
            ]
            TransactionService.objects.bulk_create(transaction_services)

        return transaction_obj

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