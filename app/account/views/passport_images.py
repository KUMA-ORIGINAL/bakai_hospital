from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers import PassportImagesSerializer


class PassportOCRView(APIView):
    serializer_class = PassportImagesSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            front_image = serializer.validated_data['front_image']
            back_image = serializer.validated_data['back_image']

            response_data = {
                "inn": '0101010101',
                "first_name": 'Асан',
                "las_name": 'Асанов',
                "patronymic": 'Асанович',
                "gender": 'male',
                'birthdate': '1999-01-01',
                'passport_number': 'ID12341232'
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
