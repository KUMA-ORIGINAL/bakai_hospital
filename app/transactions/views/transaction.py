from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from account.models import Patient
from ..models import Transaction
from ..serializers import TransactionCreateSerializer, TransactionDetailSerializer


class TransactionViewSet(viewsets.GenericViewSet,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin):
    queryset = Transaction.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionDetailSerializer

    @action(detail=False, methods=['get'], url_path='by-inn/(?P<inn>[^/.]+)')
    def by_inn(self, request, inn=None):
        try:
            patient = Patient.objects.get(inn=inn)
        except Patient.DoesNotExist:
            return Response({"detail": "Пациент с таким ИНН не найден."}, status=status.HTTP_404_NOT_FOUND)

        transactions = Transaction.objects.filter(patient=patient).order_by('-created_at')[:10]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)