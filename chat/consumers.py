import os
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from .serializers import Messageserializer
from .models import Message, Chat
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model

user = get_user_model()


class ChatConsumer(WebsocketConsumer):

    def new_message(self, data):
        print('new_message')
        message = data['message']
        author = data.get("username", None)
        room_name = data.get('room_name', None)
        self.notif(data)
        chat_model = Chat.objects.get(room_name=room_name)
        print('author', author)
        user_model = user.objects.filter(username=author).last()
        print('user_model', user_model)
        message_model = Message.objects.create(author=user_model, content=message, related_chat=chat_model)
        print(message_model)
        result = eval(self.message_serializer(message_model))
        self.send_to_chat_message(result)

    def notif(self, data):
        print("start notif")
        message_room_name = data['room_name']
        chat_room_qs = Chat.objects.filter(room_name=message_room_name)
        members_list = []
        for _ in chat_room_qs[0].members.all():
            members_list.append(_.username)

        async_to_sync(self.channel_layer.group_send)(
            'chat_listener',
            {
                'type': 'chat_message',
                'content': data['message'],
                '__str__': data['username'],
                'room_name': message_room_name,
                'members_list': members_list,
            }
        )



    def fetch_message(self, data):
        print('fetch_message')
        room_name = data['room_name']
        print('room_name', room_name)
        qs = Message.last_message(self, room_name)
        message_json = self.message_serializer(qs)
        content = {
            "message": eval(message_json),
            "command": "fetch_message",
        }

        self.chat_message(content)

    def image(self, data):
        self.send_to_chat_message(data)

    def message_serializer(self, qs):
        serialized = Messageserializer(qs,
                                       many=(lambda qs: True if (qs.__class__.__name__ == 'QuerySet') else False)(qs))
        content = JSONRenderer().render(serialized.data)
        return content

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

    commands = {
        "new_message": new_message,
        "fetch_message": fetch_message,
        "img": image,
    }

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_dict = json.loads(text_data)
        # print("text_data_dict", text_data_dict)

        command = text_data_dict['command']
        self.commands[command](self, text_data_dict)

    def send_to_chat_message(self, message):
        command = message.get("command", None)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'content': message['content'],
                'command': (lambda command: "img" if (command == "img") else "new_message")(command),
                '__str__': message['__str__']
            }
        )

    def chat_message(self, event):
        print(event)
        self.send(text_data=json.dumps(event))

# Synchronous Consumer:

# class ChatConsumer(WebsocketConsumer):
#
#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f"chat_{self.room_name}"
#
#         async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
#
#         self.accept()
#
#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
#
#     def receive(self, text_data=None, bytes_data=None):
#         text_data_dict = json.loads(text_data)
#         message = text_data_dict['message']
#
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#             }
#         )
#
#     def chat_message(self, event):
#         message = event['message']
#         self.send(text_data=json.dumps({
#             'message': message
#         }))


# ASynchronous Consumer:
# class ChatConsumer(AsyncWebsocketConsumer):
#
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f"chat_{self.room_name}"
#
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#
#     async def receive(self, text_data=None, bytes_data=None):
#         text_data_dict = json.loads(text_data)
#         message = text_data_dict['message']
#
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#             }
#         )
#
#     async def chat_message(self, event):
#         message = event['message']
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
