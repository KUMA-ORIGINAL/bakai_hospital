from rest_framework import viewsets, status
from rest_framework.response import Response

from ..models import Transaction
import logging

logger = logging.getLogger(__name__)


class PaymentWebhookViewSet(viewsets.ViewSet):
    """
    ViewSet для обработки webhook от платёжной системы.
    """
    def create(self, request, *args, **kwargs):
        try:
            data = request.data

            transaction_id = data.get('operation_id')
            payment_status = data.get('operation_state')

            if not transaction_id or not payment_status:
                logger.warning("Недостаточно данных в webhook: %s", data)
                return Response({'error': 'Недостаточно данных'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                transaction = Transaction.objects.get(id=transaction_id)
            except Transaction.DoesNotExist:
                logger.error(f"Транзакция не найдена: ID {transaction_id}")
                return Response({'error': 'Транзакция не найдена'}, status=status.HTTP_404_NOT_FOUND)

            if transaction.status != payment_status:
                logger.info(f"Обновление статуса транзакции {transaction.id}: {transaction.status} → {payment_status}")
                transaction.status = payment_status
                transaction.save(update_fields=["status"])
            else:
                logger.info(f"Повторное получение webhook: статус уже установлен — {payment_status}")

            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Ошибка при обработке webhook")
            return Response({'error': 'Внутренняя ошибка'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
