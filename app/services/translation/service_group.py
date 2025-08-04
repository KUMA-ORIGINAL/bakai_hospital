from modeltranslation.translator import TranslationOptions, register

from ..models import ServiceGroup


@register(ServiceGroup)
class ServiceGroupTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
