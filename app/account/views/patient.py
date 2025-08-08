from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import mixins
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import BaseViewSet
from ..models import Patient
from ..serializers import PatientSerializer, PatientCreateSerializer


@extend_schema(tags=['Patient',])
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                description='Поиск по INN',
                required=False,
                type=str
            )
        ]
    )
)
class PatientViewSet(BaseViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,):

    def get_serializer_class(self):
        if self.action == 'create':
            return PatientCreateSerializer
        return PatientSerializer

    def get_queryset(self):
        queryset = Patient.objects.all()
        search_query = self.request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(inn__icontains=search_query)
            )
        return queryset

    @action(detail=False, methods=['get'], url_path=r'find-by-inn/(?P<inn>\d{10,14})')
    def find_by_inn(self, request, inn=None):
        """
        Найти пациента по ИНН или вернуть 404.
        """
        patient = get_object_or_404(Patient, inn=inn)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
