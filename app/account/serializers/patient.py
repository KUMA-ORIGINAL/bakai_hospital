from rest_framework import serializers

from ..models import Patient


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = [
            'id',
            'first_name',
            'last_name',
            'patronymic',
            'inn',
            # 'birthdate',
            # 'gender',
            # 'photo',
            # 'comment',
            # 'inn',
            # 'phone_number',
            # 'passport_photo',
            # 'passport_id',
            # 'created_at',
            # 'organization',
        ]
