from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('patients', views.PatientViewSet, basename='patients')

urlpatterns = [
    path('', include(router.urls)),
    path('process-passport/', views.PassportOCRView.as_view(), name='process_passport'),
]
