import json
import logging
import re

from django.core.exceptions import RequestDataTooBig
from django.utils import translation
from django.conf import settings

logger = logging.getLogger(__name__)


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.META.get('HTTP_ACCEPT_LANGUAGE')

        if lang and lang in dict(settings.LANGUAGES):
            translation.activate(lang)
        else:
            translation.activate(settings.LANGUAGE_CODE)
        response = self.get_response(request)

        return response


class LogRequestResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_body_log_size = getattr(settings, 'MAX_BODY_LOG_SIZE', 1024 * 1024)
        self.skip_paths = getattr(settings, 'LOG_MIDDLEWARE_SKIP_PATHS', [])

    def __call__(self, request):
        if any(request.path.startswith(path) for path in self.skip_paths):
            return self.get_response(request)

        if request.path.startswith('/api/'):
            try:
                body_sample_str = self._safe_request_body(request)
                logger.info(
                    f"DRF REQUEST: method={request.method}, path={request.path}, "
                    f"content_length={request.META.get('CONTENT_LENGTH', 0)}, "
                    f"client_ip={self._get_client_ip(request)}, "
                    f"body_sample=\n{body_sample_str}"
                )
            except Exception as e:
                logger.warning(f"Failed to log request: {str(e)}", exc_info=True)

        response = self.get_response(request)

        if request.path.startswith('/api/'):
            try:
                body_sample_str = self._safe_response_body(response)
                logger.info(
                    f"DRF RESPONSE: status={response.status_code}, "
                    f"content_length={len(response.content) if hasattr(response, 'content') else 'N/A'}, "
                    f"content_type={response.get('Content-Type', '')}, "
                    f"response_sample=\n{body_sample_str}"
                )
            except Exception as e:
                logger.warning(f"Failed to log response: {str(e)}", exc_info=True)

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    def _safe_request_body(self, request):
        content_type = request.META.get("CONTENT_TYPE", "")

        # multipart/form-data — показываем только поля и имена файлов
        if "multipart/form-data" in content_type:
            try:
                fields = {k: v for k, v in request.POST.items()}
                files = {k: f.name for k, f in request.FILES.items()}
                return f"FIELDS: {json.dumps(fields, ensure_ascii=False)}, FILES: {files}"
            except RequestDataTooBig:
                return "[multipart/form-data too large to log]"
            except Exception as e:
                return f"[Failed to parse multipart body: {e}]"

        # JSON
        if "application/json" in content_type:
            try:
                body_str = request.body.decode("utf-8")
                parsed = json.loads(body_str)
                return json.dumps(parsed, ensure_ascii=False, indent=2)
            except RequestDataTooBig:
                return "[JSON body too large to log]"
            except Exception:
                return request.body[:self.max_body_log_size].decode("utf-8", errors="replace")

        # Другие текстовые типы
        if content_type.startswith("text/") or "application/x-www-form-urlencoded" in content_type:
            try:
                return request.body[:self.max_body_log_size].decode("utf-8", errors="replace")
            except RequestDataTooBig:
                return "[Text body too large to log]"
            except Exception:
                return "[Failed to decode text body]"

        return f"[Non-text body type: {content_type}]"

    def _safe_response_body(self, response):
        content_type = response.get("Content-Type", "")

        if content_type.startswith("application/json"):
            try:
                body_str = response.content.decode("utf-8")
                parsed = json.loads(body_str)
                return json.dumps(parsed, ensure_ascii=False, indent=2)
            except Exception:
                return "[Invalid JSON in response]"

        if content_type.startswith("text/"):
            return response.content[:self.max_body_log_size].decode("utf-8", errors="replace")

        return f"[BINARY DATA OMITTED: {content_type}]"