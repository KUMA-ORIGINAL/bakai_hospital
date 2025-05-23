from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from unfold.decorators import action

from account.models import ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR
from ..models import Room, Building, Department
from common.admin import BaseModelAdmin
from ..services import generate_qr_pdf


@admin.register(Room)
class RoomAdmin(BaseModelAdmin):
    search_fields = ("room_number", "building__name",)
    list_filter = ("building", "floor")
    ordering = ("room_number",)
    autocomplete_fields = ("services", 'doctors')

    actions_detail = ('download_qr_actions_detail',)

    @action(
        description="Cкачать qr-code",
        url_path="download_qr_actions_detail-url",
    )
    def download_qr_actions_detail(self, request, object_id):
        qr_url = request.build_absolute_uri(f"/rooms/{object_id}/")

        room = get_object_or_404(Room, id=object_id)

        text_department = room.department.name  # или room.department
        room_number = room.room_number  # или room.room_number

        output_pdf_stream = generate_qr_pdf(
            qr_url=qr_url,
            text_department=text_department,
            text_room=f"Кабинет №{room_number}",
            site_text="ug.imed.kg",
            scan_text_ru="Отсканируйте камерой телефона",
            pay_text_ru="Оплачивайте через:",
            scan_text_kg="Камераңыз менен сканердеңиз",
            pay_text_kg="Төлөңүз аркылуу:"
        )
        response = HttpResponse(output_pdf_stream, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="qr_code_room_id_{object_id}.pdf"'
        return response

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == ROLE_ADMIN:
            organization = request.user.organization
            if db_field.name == "building":
                kwargs["queryset"] = Building.objects.filter(organization=organization)
            if db_field.name == "department":
                kwargs["queryset"] = Department.objects.filter(organization=organization)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_list_display(self, request):
        list_display = ("id", "room_number", "floor", "building", 'department', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ("room_number", "floor", "building", 'detail_link')
        elif request.user.role in (ROLE_ACCOUNTANT, ROLE_DOCTOR):
            list_display = ("room_number", "floor", "building", 'detail_link_view')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if request.user.role == ROLE_DOCTOR:
            new_fields = []
            for field in fields:
                if field == 'building':
                    new_fields.append('building_text')
                elif field == 'department':
                    new_fields.append('department_text')
                else:
                    new_fields.append(field)
            return new_fields

        return fields

    def building_text(self, obj):
        return obj.building.name if obj.building else "-"
    building_text.short_description = "Здание"

    def department_text(self, obj):
        return obj.department.name if obj.department else "-"
    department_text.short_description = "Отдел"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR):
            return qs.filter(building__organization=request.user.organization)
        return qs
