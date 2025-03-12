from modeltranslation.translator import TranslationOptions, register

from ..models import Building


@register(Building)
class BuildingTranslationOptions(TranslationOptions):
    fields = ('name', 'address')
