import base64
import io

from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers import PassportImagesSerializer
from ..utils import send_to_openai


class PassportOCRView(APIView):
    serializer_class = PassportImagesSerializer

    @staticmethod
    def encode_image_to_base64(image, quality=50, max_size=(800, 800)):
        img = Image.open(image)
        img.thumbnail(max_size)  # Уменьшаем размер

        # Сохраняем в памяти с уменьшенным качеством
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG", quality=quality)

        return base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            front_image = serializer.validated_data['front_image']
            back_image = serializer.validated_data['back_image']

            # front_image_base64 = self.encode_image_to_base64(front_image)
            # back_image_base64 = self.encode_image_to_base64(back_image)
            #
            # response_data = send_to_openai(front_image_base64, back_image_base64)

            response_data = {
                "inn": '0101010101',
                "firstName": 'Асан',
                "lastName": 'Асанов',
                "patronymic": 'Асанович',
                "gender": 'male',
                'dateOfBirth': '1999-01-01',
                'passportNumber': 'ID12341232'
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
