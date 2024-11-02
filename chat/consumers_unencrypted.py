import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Room, Message


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room = None
        self.group_name = None
        self.room_name = None

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        self.accept()

        self.user = self.scope['user']
        self.room = Room.objects.get(name=self.room_name)

        self.room.online.add(self.user)
        self.room.save()

        last_messages = reversed(Message.objects.filter(room=self.room).order_by('-timestamp')[:50])
        for message in last_messages:
            self.send(text_data=json.dumps({
                'message': message.content
            }))

    def disconnect(self, close_code):

        if self.user.is_authenticated:
            self.room.online.remove(self.user)
            self.room.save()

        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):

        json_text = json.loads(text_data)
        message = json_text['message']


        print(f"Received message in room {self.room_name}: {json_text}")

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        room = Room.objects.get(name=self.room_name)
        Message.objects.create(user=self.user, room=room, content=json_text['message'])

    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

        print(f"Send message in room {self.room_name}: {message}")