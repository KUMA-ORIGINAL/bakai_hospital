from rest_framework import serializers

from .service import ServiceSerializer
from ..models import ServiceGroup


class ServiceGroupSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceGroup
        fields = ['id', 'name', 'description', 'total_price', 'services']
