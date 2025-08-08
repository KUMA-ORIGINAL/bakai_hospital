from rest_framework import serializers

from organizations.models import Organization
from ..models import Patient


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = (
            'id',
            'first_name',
            'last_name',
            'patronymic',
            'inn',
        )


class PatientCreateSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(
        input_formats=["%d-%m-%Y"],  # Вот здесь мы разрешаем нужный формат
        format="%Y-%m-%d"  # Формат, в котором будет возвращаться дата
    )

    class Meta:
        model = Patient
        fields = (
            'id',
            'first_name',
            'last_name',
            'patronymic',
            'phone_number',
            'inn',
            'date_of_birth',
            'gender',
            'passport_front_photo',
            'passport_back_photo',
            'passport_number',
        )
        extra_kwargs = {
            'passport_back_photo': {'required': True}
        }

    def create(self, validated_data):
        organization = Organization.objects.filter(name='Национальный Госпиталь').first()
        validated_data['organization_id'] = organization.pk
        return super().create(validated_data)
