from modeltranslation.translator import TranslationOptions, register

from ..models import Department


@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name',)
