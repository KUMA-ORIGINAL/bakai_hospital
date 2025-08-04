import requests
import logging

logger = logging.getLogger(__name__)


PAYMENT_API_URL = "https://pay.operator.kg/api/v1/payments/make-payment-link/"


def generate_payment_link(transaction):
    try:
        first_transaction_service = (
            transaction.services
            .select_related('service__payout_account')
            .first()
        )

        if not first_transaction_service:
            return None

        payout_account = first_transaction_service.service.payout_account

        if not payout_account or not payout_account.payout_token:
            return None

        payload = {
            "amount": str(transaction.total_price),
            "transaction_id": str(transaction.id),
            "comment": f"Оплата заказа #{transaction.id} hospital",
            "redirect_url": f"https://ug.imed.kg/transactions/{transaction.id}/",
            'token': payout_account.payout_token,
        }

        headers = {
            "Content-Type": "application/json",
        }

        response = requests.post(PAYMENT_API_URL, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            payment_url = data.get("pay_url")

            if payment_url:
                transaction.payment_link = payment_url
                transaction.save(update_fields=["payment_link"])

            return payment_url
        else:
            logger.error(f"Ошибка создания платёжной ссылки. Код: {response.status_code}, Ответ: {response.content}")
            return None

    except Exception as e:
        logger.error(f"Ошибка при запросе к платежному сервису: {str(e)}", exc_info=True)
        return None
