import requests
import json
import logging

from django.conf import settings

from config.settings import DOMAIN

PAYMENT_API_URL = "https://pay.operator.kg/api/v1/payments/make-payment-link/"
PAYMENT_API_TOKEN = settings.PAYMENT_API_TOKEN

logger = logging.getLogger(__name__)


def generate_payment_link(transaction):
    first_service = transaction.services.first().service
    payout_account = first_service.payout_account

    if not payout_account or not payout_account.payout_token:
        return None

    payload = {
        "amount": str(transaction.total_price),  # Итоговая сумма заказа
        "transaction_id": str(transaction.id),  # ID заказа
        "comment": f"Оплата заказа #{transaction.id} hospital",  # Комментарий
        "redirect_url": f"https://hospital.operator.kg/",
        'token': payout_account.payout_token,
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(PAYMENT_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get('pay_url')
        else:
            logger.error(f"Ошибка создания платёжной ссылки. Код: {response.status_code}, Ответ: {response.content}")
            return None

    except Exception as e:
        logger.error(f"Ошибка при запросе к платежному сервису: {str(e)}", exc_info=True)
        return None
