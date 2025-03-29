from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('transactions', views.TransactionViewSet, basename='transactions')
router.register('payment/webhook', views.PaymentWebhookViewSet, basename='payment_webhook')


urlpatterns = [
    path('', include(router.urls)),
]
