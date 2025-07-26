import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PresenceConsumer(AsyncWebsocketConsumer):
    active_users = set()  # Works per process

    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            self.username = user.username
            PresenceConsumer.active_users.add(self.username)

            await self.channel_layer.group_add("presence", self.channel_name)
            await self.accept()

            # Notify everyone this user came online
            await self.channel_layer.group_send(
                "presence",
                {
                    "type": "user_status",
                    "username": self.username,
                    "status": "online",
                }
            )

            # Send full list of active users to current user
            await self.send_active_users()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "username"):
            PresenceConsumer.active_users.discard(self.username)
            await self.channel_layer.group_discard("presence", self.channel_name)

            await self.channel_layer.group_send(
                "presence",
                {
                    "type": "user_status",
                    "username": self.username,
                    "status": "offline",
                }
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "get_active_users":
            await self.send_active_users()

    async def send_active_users(self):
        await self.send(text_data=json.dumps({
            "type": "active_users",
            "users": list(PresenceConsumer.active_users)
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_status",
            "username": event["username"],
            "status": event["status"],
        }))
