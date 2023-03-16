# arena/consumers.py
import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache


class ArenaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"].username
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        print("User: ", user, "connected to: ", self.room_name)
        self.room_group_name = "arena_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Add users to onlineUsers only when connect to ARENA group
        if self.room_name == "ARENA":
            online_users = []
            if not user in online_users:
                online_users.append(user)
            cache.set("onlineUsers", online_users)
            print(f"Online users: {online_users}")

            json_mes = {"type": "user_online_message", "message_type": "user_online_status_message", "username": user, "user_connected": True}
            await self.channel_layer.group_send(self.room_group_name, json_mes)

    async def disconnect(self, close_code):
        # Leave room group
        user = self.scope["user"].username
        room_name = self.scope["url_route"]["kwargs"]
        print("User: ", user, "disconnected from: ", room_name)

        if self.room_name == "ARENA":
            online_users = cache.get("onlineUsers")
            if user in online_users:
                del online_users[online_users.index(user)]
            cache.set("onlineUsers", online_users)
            print(f"Online users: {online_users}")

            # remove open matches from Cache
            open_matches = cache.get("openMatches")
            new_open_matches = []
            delete_matches = []
            for match, games_host in open_matches:
                if user == games_host:
                    print(f"Game {match} removed from DB!")
                    delete_matches.append(match)
                else:
                    new_open_matches.append((match, games_host))
            cache.set("openMatches", new_open_matches)
            print("OpenMatches Updated in DB: ", new_open_matches)
            print("Delete matches: ", delete_matches)
            json_mes = {"type": "user_online_message", "message_type": "user_online_status_message", "username": user,
                        "user_connected": False, "delete_matches": delete_matches}
            await self.channel_layer.group_send(self.room_group_name, json_mes)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("Received: ", text_data_json)
        username = self.scope["user"].username
        message_super_type = text_data_json["type"]

        # NEW MATCH REQUEST
        if message_super_type == "new_match_create":
            # get existing match requests from cache
            open_matches = cache.get("openMatches")
            open_matches = [] if open_matches is None else open_matches

            # check if user has an open match request
            hosts = [host for _, host in open_matches]
            if username in hosts:
                message = f"Hey, {username} already has an open match request!"
                # send chat response
                print(message)
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "arena_message", "message_type": "chat", "message": message, "username": "rev3rsi"}
                )
            else:
                # open new match
                game_uuid = str(uuid.uuid4())
                print(f"New Match creation request, creating match with with id {game_uuid}")
                # add match to cache
                open_matches.append((game_uuid, username))
                # cache.set('openMatches', open_matches, 30)
                cache.set('openMatches', open_matches)
                print("Match added to cache, OpenMatches:", open_matches)

                # Send game request to room group
                json_resp = {"type": "arena_message", "message_type": "add_new_match", "message": "",
                             "game_uuid": game_uuid, "host": username}
                print("Sending to room group:", json_resp)
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name, json_resp)

        # NEW MATCH ACCEPT
        elif message_super_type == "new_match_accept":
            game_id = text_data_json["game_id"]
            game_uuid = text_data_json["game_uuid"]
            host = text_data_json["host"]
            print(f'{game_uuid} with game_id {game_id} (hosted by: {host}), accepted by {username}!')

            # remove open matches from Cache
            open_matches = cache.get("openMatches")
            new_open_matches = []
            delete_matches = []
            for match, games_host in open_matches:
                if username == games_host or match == game_uuid:
                    print(f"Game {match} removed from DB!")
                    delete_matches.append(match)
                else:
                    new_open_matches.append((match, games_host))
            cache.set("openMatches", new_open_matches)
            print("OpenMatches Updated in DB: ", new_open_matches)
            print("Delete matches: ", delete_matches)

            json_resp = {"type": "arena_message", "message_type": "new_match_confirmed",
                         "game_id": game_id, 'game_uuid': game_uuid, "username": username, "host": host,
                         "delete_matches": delete_matches,
                         }
            print("Sending to room group:", json_resp)
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, json_resp)


        elif message_super_type == "match_turn":
            print("NEW TURN event received!")
            message = text_data_json["message"]
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "arena_message", "message_type": "match_turn_cast", "message": message,
                                       "player": username}
            )

        # CHAT TEXT MESSAGE
        elif message_super_type == "chat_text_message":
            message = text_data_json["message"]
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "arena_message", "message_type": "chat", "message": message, "username": username}
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


    # Relay message to room group
    async def user_online_message(self, event):
        message_type = event["message_type"]
        user_connected = event.get("user_connected")
        username = event.get("username")
        delete_matches = event.get("delete_matches")

        json_resp = {"message_type": message_type,
                     "username": username, "user_connected": user_connected, "delete_matches": delete_matches}
        print("Group BROADCAST message: ", json_resp)

        # Send message to WebSocket
        await self.send(text_data=json.dumps(json_resp))