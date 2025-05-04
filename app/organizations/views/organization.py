from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins

from organizations.models import Organization
from organizations.serializers import OrganizationSerializer


@extend_schema(
    tags=['Organization'],
)
class OrganizationViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
