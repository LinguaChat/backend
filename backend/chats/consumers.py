# import base64
import json

# from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Message, PersonalChat
from .serializers import MessageSerializer

# import secrets
# from datetime import datetime

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        if isinstance(self.scope["user"], AnonymousUser):
            self.close()

        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        # parse the json data into dictionary object
        text_data_json = json.loads(text_data)

        # Send message to room group
        chat_type = {"type": "chat_message"}
        return_dict = {**chat_type, **text_data_json}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            return_dict,
        )

    # Receive message from room group
    def chat_message(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")
        message, attachment = (
            text_data_json["message"],
            text_data_json.get("attachment", None),
        )

        chat = PersonalChat.objects.get(id=int(self.chat_id))
        sender = self.scope['user']

        # Attachment
        if attachment:
            pass
        #     file_str, file_ext = attachment["data"], attachment["format"]

        #     file_data = ContentFile(
        #         base64.b64decode(file_str),
        #         name=f"{secrets.token_hex(8)}.{file_ext}"
        #     )
        #     _message = Message.objects.create(
        #         sender=sender,
        #         attachment=file_data,
        #         text=message,
        #         chat=chat,
        #     )
        # else:
        _message = Message.objects.create(
            sender=sender,
            text=message,
            chat=chat,
        )
        serializer = MessageSerializer(instance=_message)
        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                serializer.data
            )
        )
