from rest_framework import viewsets, mixins

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
