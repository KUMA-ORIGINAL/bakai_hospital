from django.http import JsonResponse
from rest_framework import viewsets

from ..models import Service
from ..serializers import ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


def get_services_by_category(request):
    ids = request.GET.get('category_ids', '')  # "1,2,3"
    if not ids:
        return JsonResponse({'services': []})

    id_list = [int(pk) for pk in ids.split(',') if pk]
    services = Service.objects.filter(category_id__in=id_list)

    return JsonResponse({
        'services': list(services.values('id', 'name'))
    })
