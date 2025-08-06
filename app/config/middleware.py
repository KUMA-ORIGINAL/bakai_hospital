import logging

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

    def __call__(self, request):
        logger.info(f"REQUEST: path={request.path}, body={request.body}")
        response = self.get_response(request)
        logger.info(f"RESPONSE: status={response.status_code}, content={response.content}")
        return response
