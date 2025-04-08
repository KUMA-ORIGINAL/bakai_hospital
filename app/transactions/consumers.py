import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TransactionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.transaction_id = self.scope["url_route"]["kwargs"]["transaction_id"]
        self.group_name = f"transaction_{self.transaction_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def transaction_status_updated(self, event):
        await self.send(text_data=json.dumps({
            "transaction_id": event["transaction_id"],
            "status": event["status"],
        }))