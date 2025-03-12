from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from django.db.models import Q

from ..models import Patient
from ..serializers import PatientSerializer


@extend_schema(
    tags=['Patient'],
    parameters=[
        OpenApiParameter(
            name='search',  # Имя параметра
            description='Поиск по INN',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        )
    ]
)
class PatientViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        """
        Определяет поиск по параметрам phone_number и inn.
        """
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(inn__icontains=search_query)
            )
        return queryset