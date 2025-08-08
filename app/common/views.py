import json
import logging
import time

from rest_framework import viewsets

logger = logging.getLogger(__name__)


class RequestResponseLogMixin:
    LOG_MAX = 2000
    SENSITIVE = {'password', 'token', 'access', 'refresh', 'secret', 'authorization'}

    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)
        try:
            drf_request._log_started_at = time.time()
        except Exception:
            pass
        return drf_request

    def _mask_value(self, k, v):
        if k.lower() in self.SENSITIVE:
            return '***'
        s = str(v)
        return s if len(s) <= self.LOG_MAX else s[: self.LOG_MAX] + '…'

    def _prepare_dict(self, d):
        if d is None:
            return None
        try:
            out = {}
            # d может быть QueryDict
            items = d.items() if hasattr(d, 'items') else dict(d).items()
            for k, v in items:
                out[k] = self._mask_value(k, v)
            return out
        except Exception:
            return str(d)

    def finalize_response(self, request, response, *args, **kwargs):
        try:
            duration_ms = None
            try:
                duration_ms = int((time.time() - getattr(request, '_log_started_at', time.time())) * 1000)
            except Exception:
                pass

            # ВАЖНО: здесь request — это DRF Request с уже распарсенными data/FILES
            req_data = None
            files_info = {}
            try:
                req_data = self._prepare_dict(getattr(request, 'data', None))
                if hasattr(request, 'FILES'):
                    # Только имена и размеры файлов, без чтения содержимого
                    for k, file_list in request.FILES.lists():
                        files_info[k] = [{'name': f.name, 'size': getattr(f, 'size', None)} for f in file_list]
            except Exception:
                pass

            # Ответ
            resp_sample = None
            try:
                if hasattr(response, 'data'):
                    # До рендера доступно response.data
                    resp_sample = response.data
                else:
                    # Нестрогий fallback
                    ct = response.get('Content-Type', '')
                    if ct.startswith('application/json'):
                        resp_sample = json.loads(response.content.decode('utf-8'))
                    elif ct.startswith('text/'):
                        body = response.content.decode('utf-8', errors='replace')
                        resp_sample = body[: self.LOG_MAX]
                    else:
                        resp_sample = f'[binary {ct}]'
            except Exception:
                resp_sample = '[unavailable]'

            logger.info(json.dumps({
                'method': request.method,
                'path': request.get_full_path(),
                'data': req_data,
                'files': files_info,
                'status': getattr(response, 'status_code', None),
                'duration_ms': duration_ms,
                'response': resp_sample,
            }, ensure_ascii=False))
        except Exception:
            logger.exception('Failed to log request/response')
        return super().finalize_response(request, response, *args, **kwargs)


class BaseViewSet(RequestResponseLogMixin, viewsets.GenericViewSet):
    pass
