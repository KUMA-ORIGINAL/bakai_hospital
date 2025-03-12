from rest_framework import serializers

from ..models import User


# class UserSerializer(serializers.ModelSerializer):
#     services = ServiceSerializer(many=True, read_only=True)
#     room = RoomSerializer(read_only=True)
#     department = DepartmentSerializer(read_only=True)
#     building = BuildingSerializer(source='room.building', read_only=True)
#
#     class Meta:
#         model = User
#         fields = [
#             'id', 'first_name', 'last_name', 'patronymic', 'position', 'photo', 'department', 'building', 'room', 'services'
#         ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'patronymic', 'position', 'photo'
        ]
