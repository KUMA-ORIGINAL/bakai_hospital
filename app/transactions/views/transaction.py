from django.db.models import Prefetch
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from account.models import Patient
from ..models import Transaction, TransactionService
from ..serializers import TransactionCreateSerializer, TransactionDetailSerializer


class TransactionViewSet(viewsets.GenericViewSet,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin):

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionDetailSerializer

    def get_queryset(self):
        queryset = Transaction.objects.select_related('staff', 'patient', 'organization') \
            .prefetch_related(Prefetch(
                'services',
                queryset=TransactionService.objects.select_related('service')
            ))
        return queryset

    @action(detail=False, methods=['get'], url_path='by-inn/(?P<inn>[^/.]+)')
    def by_inn(self, request, inn=None):
        try:
            patient = Patient.objects.get(inn=inn)
        except Patient.DoesNotExist:
            return Response({"detail": "Пациент с таким ИНН не найден."}, status=status.HTTP_404_NOT_FOUND)

        transactions = (
            Transaction.objects
            .filter(patient=patient, status='success')
            .select_related('patient', 'staff')  # ForeignKey
            .prefetch_related(
                Prefetch(
                    'services',  # related_name в модели TransactionService
                    queryset=TransactionService.objects.select_related('service')
                )
            )
            .order_by('-created_at')[:10]
        )

        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)