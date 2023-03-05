# chat/consumers.py
import json
import uuid
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer

import redis
conn = redis.Redis('localhost')


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

        if text_data_json["type"] == "new_game_create":
            #game_uuid = username + "_vs_"
            game_uuid = str(datetime.now()).replace("-", "").replace(":", "").replace(" ", "").replace(".", "")
            print(f"New Match creation request, creating match with with id {game_uuid}")
            open_matches = conn.hgetall("openMatches")
            open_matches.update({game_uuid: username})
            conn.hmset("openMatches", open_matches)

            # Send game request to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message_type": "add_new_match", "message": "", "game_id": game_uuid, "username": username}
            )
        elif text_data_json["type"] == "chat_message":
            message = text_data_json["message"]
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message_type": "chat", "message": message, "username": username}
            )
        elif text_data_json["type"] == "new_game_accept":
            game_id = text_data_json["game_id"]
            game_name = text_data_json["game_name"]
            host = text_data_json["host"]
            print(f'{game_name} with game_id {game_id} (hosted by: {host}), accepted by {username}!')

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat_message", "message_type": "new_game_confirmed", "game_id": game_id,
                 'game_name': game_name, "username": username, "host": host}
            )
            # Flush Redis DB
            conn.flushdb()
            """
            # remove from Redis DB
            open_matches = conn.hgetall("openMatches")
            new_open_matches = {}
            for match in open_matches:
                name = match.decode("utf-8")
                host = open_matches.get(match).decode("utf-8")
                print(name+username, game_name)
                if not name+username == game_name:
                    new_open_matches.update({name: host})
            print(f"Redis DB update with: {new_open_matches}")
            conn.hmset("openMatches", new_open_matches)
            """

        elif text_data_json["type"] == "new_game_turn":
            message = text_data_json["message"]
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message_type": "game_turn", "message": message}
            )


    # Receive message from room group
    async def chat_message(self, event):
        print("Group Received: ", event)
        message_type = event["message_type"]
        game_id = event.get("game_id")
        message = event.get("message")
        username = event.get("username")
        game_name = event.get("game_name")
        host = event.get("host")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "message_type": message_type, "username": username,
                                              "game_id": game_id, "game_name": game_name, "host": host}))
