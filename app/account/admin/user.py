from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from organizations.models import Room, Department
from ..models import User, ROLE_ADMIN

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(GroupAdmin, UnfoldModelAdmin):
    pass


@admin.register(User)
class UserAdmin(UserAdmin, UnfoldModelAdmin):
    model = User
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display_links = ('id', 'email')
    search_fields = ('email', 'first_name', 'last_name', 'role')  # Поля для поиска
    ordering = ('-date_joined',)  # Сортировка по дате присоединения
    list_per_page = 20

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def get_list_filter(self, request):
        list_filter = ('role', 'status', 'is_active', 'is_staff')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_filter = ('role', 'status')
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'status', 'organization')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ('email', 'first_name', 'last_name', 'role', 'status')
        return list_display

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {"fields": ("email", "password", 'role', 'status')}),
            (
                "Permissions",
                {
                    "fields": (
                        "is_staff",
                        "is_active",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    )
                },
            ),
            ("Dates", {"fields": ("last_login", "date_joined")}),
            ('Personal info', {'fields': (
                'first_name', 'last_name', 'patronymic', 'birthdate', 'phone_number', 'telegram_id', 'comment',
                'photo')}),
            ('Organization', {'fields': ('organization', 'room', 'department')}),
        )
        if request.user.is_superuser:
            pass

        elif request.user.role == ROLE_ADMIN:
            fieldsets = [fs for fs in fieldsets if fs[0] != "Permissions"]
            fieldsets[3][1]['fields'] = ('room', 'department')
        return fieldsets

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == ROLE_ADMIN:
            organization = request.user.organization
            if db_field.name == "room":
                kwargs["queryset"] = Room.objects.filter(building__organization=organization)
            elif db_field.name == "department":
                kwargs["queryset"] = Department.objects.filter(organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(organization=request.user.organization)
