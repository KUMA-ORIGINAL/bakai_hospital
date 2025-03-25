from rest_framework import serializers

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

    class Meta:
        model = Patient
        fields = (
            'id',
            'first_name',
            'last_name',
            'patronymic',
            'inn',
            'date_of_birth',
            'gender',
            'passport_front_photo',
            'passport_back_photo',
            'passport_number',
        )
