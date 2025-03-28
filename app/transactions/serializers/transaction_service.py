from rest_framework import serializers

from ..models import TransactionService


class TransactionServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = TransactionService
        fields = ['id', 'service', 'service_name', 'service_price']
