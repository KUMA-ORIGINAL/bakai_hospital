from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RoomViewSet, OrganizationViewSet


router = DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'organizations', OrganizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
