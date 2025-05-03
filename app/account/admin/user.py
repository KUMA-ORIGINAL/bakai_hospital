from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm as BaseUserChangeForm, UserCreationForm, \
    UnfoldReadOnlyPasswordHashWidget

from common.admin import BaseModelAdmin
from organizations.models import Room
from ..models import User, ROLE_ADMIN, ROLE_ACCOUNTANT

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(GroupAdmin, UnfoldModelAdmin):
    pass


class MaskedPasswordWidget(UnfoldReadOnlyPasswordHashWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        usable_password = value and not value.startswith(UNUSABLE_PASSWORD_PREFIX)

        if usable_password:
            context["summary"] = [
                {"label": "*****************************************************************************************"},
            ]
        else:
            context["summary"] = [
                {"label": _("No password set.")},
            ]

        context["button_label"] = (
            _("Reset password") if usable_password else _("Set password")
        )
        return context


class UserChangeForm(BaseUserChangeForm):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password"].widget = MaskedPasswordWidget()


@admin.register(User)
class UserAdmin(UserAdmin, BaseModelAdmin):
    model = User
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm
    add_form = UserCreationForm

    list_display_links = ('id', 'email')
    search_fields = ('email', 'first_name', 'last_name', 'role')
    ordering = ('-date_joined',)
    autocomplete_fields = ('groups',)
    list_per_page = 20

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', "first_name", "last_name",),
        }),
    )

    def get_list_filter(self, request):
        list_filter = ('role', 'status', 'is_active', 'is_staff',)
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_filter = ('role', 'status')
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'position', 'specialization', 'status', 'organization', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ('email', 'first_name', 'last_name', 'role', 'position', 'specialization', 'status', 'detail_link')
        return list_display

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets

        fieldsets = [
            (None, {
                "fields": ("email", "password"),
            }),
            ("Права доступа", {
                "fields": ("is_staff", "is_active", "is_superuser", "groups",),
            }),
            ("Даты", {
                "fields": ("last_login", "date_joined"),
            }),
            ("Личная информация", {
                "fields": (
                    "first_name", "last_name", "patronymic", "role", "status", "birthdate", "phone_number",
                    "position", "specialization", "telegram_id", "comment", "photo"
                ),
            }),
            ("Организация", {
                "fields": ("organization",),
            }),
        ]

        if not request.user.is_superuser and request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT):
            fieldsets = [fs for fs in fieldsets if fs[0] != "Права доступа" or fs[0] != 'Организация']
        return fieldsets

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization
            obj.is_staff = True
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT):
            return qs.filter(organization=request.user.organization)
        return qs