from rest_framework import serializers


class PassportImagesSerializer(serializers.Serializer):
    front_image = serializers.ImageField()
    back_image = serializers.ImageField()
