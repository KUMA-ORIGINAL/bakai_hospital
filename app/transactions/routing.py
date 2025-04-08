from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/transactions/<int:transaction_id>/", consumers.TransactionConsumer.as_asgi()),
]