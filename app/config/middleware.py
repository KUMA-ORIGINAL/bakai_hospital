import json
import logging

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
        # Skip logging for certain paths
        if any(request.path.startswith(path) for path in self.skip_paths):
            return self.get_response(request)

        if request.path.startswith('/api/'):
            content_length = int(request.META.get('CONTENT_LENGTH', 0) or 0)
            try:
                try:
                    body_sample = request.body
                except RequestDataTooBig:
                    body_sample = b'[Request body too large to log]'
                # Обрезаем если слишком большой
                if isinstance(body_sample, bytes) and len(body_sample) > self.max_body_log_size:
                    body_sample = body_sample[:self.max_body_log_size] + b'...[truncated]'
                # Декодируем для лога
                content_type = request.META.get("CONTENT_TYPE", "")
                body_sample_str = self._format_body_for_log(body_sample, content_type)
                logger.info(
                    f"DRF REQUEST: method={request.method}, path={request.path}, "
                    f"content_length={content_length}, "
                    f"client_ip={self._get_client_ip(request)}, "
                    f"body_sample=\n{body_sample_str}"
                )
            except Exception as e:
                logger.warning(f"Failed to log request: {str(e)}", exc_info=True)

        response = self.get_response(request)

        if request.path.startswith('/api/'):
            try:
                response_sample = response.content
                if isinstance(response_sample, bytes) and len(response_sample) > self.max_body_log_size:
                    response_sample = response_sample[:self.max_body_log_size] + b'...[truncated]'
                content_type = response.get('Content-Type', '')
                response_sample_str = self._format_body_for_log(response_sample, content_type)
                content_length = len(response.content)
                logger.info(
                    f"DRF RESPONSE: status={response.status_code}, "
                    f"content_length={content_length}, "
                    f"content_type={content_type}, "
                    f"response_sample=\n{response_sample_str}"
                )
            except Exception as e:
                logger.warning(f"Failed to log response: {str(e)}", exc_info=True)
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _format_body_for_log(self, body: bytes, content_type: str = 'application/json') -> str:
        try:
            body_str = body.decode('utf-8')
            if 'application/json' in content_type:
                # Попробуйте отформатировать JSON красиво
                try:
                    parsed = json.loads(body_str)
                    return json.dumps(parsed, ensure_ascii=False, indent=2)
                except Exception:
                    return body_str  # Не парсится как JSON, просто строка
            return body_str
        except Exception:
            return repr(body)  # Не декодируется, оставьте как есть
