from modeltranslation.translator import TranslationOptions, register

from ..models import Organization


@register(Organization)
class OrganizationTranslationOptions(TranslationOptions):
    fields = ('name', 'address')

