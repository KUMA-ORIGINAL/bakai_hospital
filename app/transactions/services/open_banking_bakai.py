import requests
import json
import logging

from django.conf import settings

from config.settings import DOMAIN

PAYMENT_API_URL = "https://openbanking-api.bakai.kg/api/PayLink/CreatePayLink"
PAYMENT_API_TOKEN = settings.PAYMENT_API_TOKEN

logger = logging.getLogger(__name__)


def generate_payment_link(transaction):
    payload = {
        "amount": str(transaction.total_price),  # Итоговая сумма заказа
        "transactionID": str(transaction.id),  # ID заказа
        "comment": f"Оплата заказа #{transaction.id}",  # Комментарий
        "redirectURL": f"https://hospital.mnogo.kg/api/payment/webhook/"  # URL после успешной оплаты
    }

    headers = {
        "Content-Type": "application/json",
        'accept': '*/*',
        'Authorization': f"Bearer {PAYMENT_API_TOKEN}"
    }

    try:
        response = requests.post(PAYMENT_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            return response.text.strip()
        else:
            logger.error(f"Ошибка создания платёжной ссылки. Код: {response.status_code}, Ответ: {response.content}")
            return None

    except Exception as e:
        logger.error(f"Ошибка при запросе к платежному сервису: {str(e)}", exc_info=True)
        return None
