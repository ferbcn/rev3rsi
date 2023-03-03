# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connected: ", self.scope["url_route"]["kwargs"])
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("Received: ", text_data_json)
        username = self.scope["user"].username

        if text_data_json["type"] == "newgame_message":
            game_name = text_data_json["message"]
            print(f"New Game creation request with name {game_name}")
            # Send game request to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message_type": "new_game", "message": game_name, "username": username}
            )
        elif text_data_json["type"] == "chat_message":
            message = text_data_json["message"]
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message_type": "chat", "message": message, "username": username}
            )

        elif text_data_json["type"] == "newgame_accept":
            message = text_data_json["message"]
            host = text_data_json["host"]
            print(f'{message} (hosted by: {host}), accepted by {username}!')


    # Receive message from room group
    async def chat_message(self, event):
        print("Group Received: ", event)
        message = event["message"]
        username = event["username"]
        message_type = event["message_type"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "message_type": message_type, "username": username}))
