from rest_framework import serializers
from organizations.models import Room

from account.serializers import UserSerializer
from services.serializers import ServiceSerializer

from .department import DepartmentSerializer
from .building import BuildingSerializer


class RoomSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    doctors = UserSerializer(many=True, read_only=True, source='user_set')
    building = BuildingSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'floor', 'building', 'department', 'services', 'doctors']
