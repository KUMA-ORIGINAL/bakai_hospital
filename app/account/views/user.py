from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Lower
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins

from ..models import User
from ..serializers import UserSerializer


@extend_schema(
    tags=['Staff'],
    parameters=[
        OpenApiParameter(
            name='room_id',
            description='Фильтр по id кабинета',
            required=False,
            type=int
        ),
        OpenApiParameter(
            name='search',
            description='Поиск по ФИО staff',
            required=False,
            type=str
        )
    ]
)
class UserViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = (User.objects.select_related('organization', 'room').prefetch_related('services')
                    .filter(role=User.ROLE_DOCTOR))
        search_query = self.request.GET.get("search")
        room_id = self.request.GET.get("room_id")

        if room_id:
            queryset = queryset.filter(room_id=room_id)

        if search_query:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity(Lower('first_name', 'last_name', 'patronymic'), search_query.lower()),
            ).filter(similarity__gt=0.1).order_by('-similarity')

        return queryset
