from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins

from organizations.models import Room
from organizations.serializers import RoomSerializer


@extend_schema(
    tags=['Rooms'],
)
class RoomViewSet(viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin):
    queryset = Room.objects.prefetch_related('services', 'user_set').all()
    serializer_class = RoomSerializer

