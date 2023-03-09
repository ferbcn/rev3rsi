# arena/consumers.py
import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
import os

REDIS_HOST = os.environ.get("REDIS_HOST")
conn = redis.Redis(REDIS_HOST)


class ArenaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("User: ", self.scope["user"].username, "connected to: ", self.scope["url_route"]["kwargs"])
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "arena_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        print("User: ", self.scope["user"].username, "disconnected from: ", self.scope["url_route"]["kwargs"])
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("Received: ", text_data_json)
        username = self.scope["user"].username
        message_super_type = text_data_json["type"]

        if message_super_type == "new_match_create":
            # game_uuid = str(datetime.now()).replace("-", "").replace(":", "").replace(" ", "").replace(".", "")
            # check for existing matches ba user
            open_matches = conn.hgetall("openMatches")
            # check if user has an open match request
            hosts = [name.decode("utf-8") for name in list(open_matches.values())]

            if username in hosts:
                print("User already has an open match request!")
            else:
                # else open new match
                game_uuid = str(uuid.uuid4())
                print(f"New Match creation request, creating match with with id {game_uuid}")

                # Send game request to room group
                json_resp = {"type": "arena_message", "message_type": "add_new_match", "message": "",
                             "game_uuid": game_uuid, "host": username}

                print("Sending to room group:", json_resp)
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name, json_resp)

                open_matches.update({game_uuid: username})
                conn.hmset("openMatches", open_matches)
                print("Match added to OpenMatches, OpenMatches:", open_matches)


        elif message_super_type == "chat_text_message":
            message = text_data_json["message"]
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "arena_message", "message_type": "chat", "message": message, "username": username}
            )

        elif message_super_type == "new_match_accept":
            game_id = text_data_json["game_id"]
            game_uuid = text_data_json["game_uuid"]
            host = text_data_json["host"]
            print(f'{game_uuid} with game_id {game_id} (hosted by: {host}), accepted by {username}!')
            open_matches = conn.hgetall("openMatches")
            # delete_matches = [host.decode("utf-8") for host in open_matches]

            # remove open matches from Redis DB
            new_open_matches = {}
            delete_matches = []
            for match, games_host in open_matches.items():
                match_deco = match.decode("utf-8")
                host_deco = games_host.decode("utf-8")
                if username == host_deco or match_deco == game_uuid:
                    print(f"Game {match_deco} removed from DB!")
                    delete_matches.append(match_deco)
                else:
                    new_open_matches.update({match_deco: host_deco})
            print("OpenMatches Updated in DB: ", new_open_matches)

            json_resp = {"type": "arena_message", "message_type": "new_match_confirmed",
                         "game_id": game_id, 'game_uuid': game_uuid, "username": username, "host": host,
                         "delete_matches": delete_matches,
                         }
            print("Sending to room group:", json_resp)
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, json_resp)

            # Redis DB: flush and save open matches
            conn.flushdb()
            if len(new_open_matches) > 0:
                conn.hmset("openMatches", new_open_matches)

        elif message_super_type == "match_turn":
            print("NEW TURN event received!")
            message = text_data_json["message"]
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "arena_message", "message_type": "match_turn_cast", "message": message,
                                       "player": username}
            )

    # Relay message to room group
    async def arena_message(self, event):
        message_type = event["message_type"]
        game_id = event.get("game_id")
        message = event.get("message")
        username = event.get("username")
        game_uuid = event.get("game_uuid")
        host = event.get("host")
        delete_matches = event.get("delete_matches")
        player = event.get("player")

        json_resp = {"message_type": message_type, "message": message, "username": username,
                     "game_id": game_id, "game_uuid": game_uuid, "host": host, "player": player,
                     "delete_matches": delete_matches}
        print("Group BROADCAST message: ", json_resp)

        # Send message to WebSocket
        await self.send(text_data=json.dumps(json_resp))
