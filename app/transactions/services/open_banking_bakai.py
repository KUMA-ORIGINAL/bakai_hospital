import json
import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

PAYMENT_API_URL = "https://pay.operator.kg/api/v1/payments/make-payment-link/"
REQUEST_TIMEOUT = 15
RETRY_TOTAL = 3
RETRY_BACKOFF = 0.5

_SESSION: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is not None:
        return _SESSION

    session = requests.Session()
    retry = Retry(
        total=RETRY_TOTAL,
        read=RETRY_TOTAL,
        connect=RETRY_TOTAL,
        status=RETRY_TOTAL,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["POST", "GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    _SESSION = session
    return session


def _amount_to_str(value) -> str:
    try:
        dec = Decimal(value)
    except (InvalidOperation, TypeError):
        raise ValueError(f"Invalid amount: {value!r}")
    quantized = dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(quantized, "f")


def _safe_resp_text(resp: Response) -> str:
    try:
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception:
        try:
            return resp.text[:2000]
        except Exception:
            return "<unreadable>"


def generate_payment_link(transaction, *, redirect_base: str = "https://ug.imed.kg/transactions/") -> Optional[str]:
    try:
        tx_id = str(transaction.id)
        first_tx_service = (
            transaction.services.select_related("service__payout_account").order_by("id").first()
        )
        if not first_tx_service:
            logger.warning("generate_payment_link: нет services у транзакции id=%s", tx_id)
            return None

        payout_account = getattr(first_tx_service.service, "payout_account", None)
        payout_token = getattr(payout_account, "payout_token", None)
        if not payout_token:
            logger.warning("generate_payment_link: отсутствует payout_token для транзакции id=%s", tx_id)
            return None

        try:
            amount_str = _amount_to_str(transaction.total_price)
        except ValueError as e:
            logger.error("generate_payment_link: некорректная сумма для транзакции id=%s: %s", tx_id, e)
            return None

        payload = {
            "amount": amount_str,
            "transaction_id": tx_id,
            "comment": f"Оплата заказа #{tx_id} hospital",
            "redirect_url": f"{redirect_base.rstrip('/')}/{tx_id}/",
            "token": payout_token,
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        session = _get_session()
        resp = session.post(PAYMENT_API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)

        if not resp.ok:
            logger.error(
                "generate_payment_link: API вернул ошибку. status=%s, tx_id=%s, body=%s",
                resp.status_code, tx_id, _safe_resp_text(resp)
            )
            return None

        try:
            data = resp.json()
        except json.JSONDecodeError:
            logger.error("generate_payment_link: невалидный JSON от API. tx_id=%s, text=%s", tx_id, resp.text[:2000])
            return None

        payment_url = data.get("pay_url") or data.get("payUrl")
        if not payment_url:
            logger.error("generate_payment_link: в ответе нет pay_url. tx_id=%s, data=%s", tx_id, data)
            return None

        try:
            transaction.payment_link = payment_url
            transaction.save(update_fields=["payment_link"])
        except Exception:
            logger.exception("generate_payment_link: не удалось сохранить payment_link в транзакцию id=%s", tx_id)

        return payment_url

    except requests.Timeout:
        logger.error("generate_payment_link: timeout при обращении к API. tx_id=%s", getattr(transaction, "id", "?"))
        return None
    except requests.RequestException as e:
        logger.error("generate_payment_link: ошибка сети при обращении к API. tx_id=%s, err=%s",
                     getattr(transaction, "id", "?"), e)
        return None
    except Exception:
        logger.exception("generate_payment_link: непредвиденная ошибка. tx_id=%s", getattr(transaction, "id", "?"))
        return None
