import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Room, Message
from .rsa import *


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room = None
        self.group_name = None
        self.room_name = None
        self.rsa_d_cookie_value = None
        self.rsa_n_cookie_value = None

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f'chat_{self.room_name}'

        try:
            self.rsa_d_cookie_value = int(self.scope['cookies'].get('rsa_priv_key_d'))
            self.rsa_n_cookie_value = int(self.scope['cookies'].get('rsa_priv_key_n'))

            if not self.rsa_d_cookie_value or not self.rsa_n_cookie_value:
                print("Clés RSA manquantes")
                self.close()
                return
        except ValueError:
            print("Erreur: Clés RSA non valides")
            self.close()
            return
        except Exception as e:
            print(f"Erreur: {e}")
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

        self.user = self.scope['user']
        self.room = Room.objects.get(name=self.room_name)

        self.room.online.add(self.user)
        self.room.save()

        last_messages = reversed(Message.objects.filter(room=self.room).order_by('-timestamp')[:50])
        for message in last_messages:
            try:
                if self.user == message.user:
                    m = message_decrypt(int(message.content_sender), self.rsa_d_cookie_value, self.rsa_n_cookie_value)
                else:
                    m = message_decrypt(int(message.content_receiver), self.rsa_d_cookie_value, self.rsa_n_cookie_value)
                decrypted_message = int_to_str(m)
                self.send(text_data=json.dumps({
                    'user': str(message.user),
                    'message': decrypted_message,
                    'time': str(message.timestamp.strftime('%d.%m.%Y, %H:%M:%S'))
                }
                ))
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")

    def disconnect(self, close_code):

        if self.user.is_authenticated:
            self.room.online.remove(self.user)
            self.room.save()

        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        try:
            json_text = json.loads(text_data)
            message_sender = json_text['message_sender']
            message_receiver = json_text['message_receiver']

            # print(f"Message sender reçu dans la room {self.room_name}: {message_sender}")
            # print(f"Message receiver reçu dans la room {self.room_name}: {message_sender}")

            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    'type': 'chat_message',
                    'user': self.user,
                    'message_sender': message_sender,
                    'message_receiver': message_receiver,
                    'time': datetime.now().strftime('%d.%m.%Y, %H:%M:%S'),
                }
            )

            room = Room.objects.get(name=self.room_name)
            Message.objects.create(user=self.user, room=room, content_sender=message_sender, content_receiver=message_receiver)

        except Exception as e:
            print(f"Erreur lors de la réception du message : {e}")

    def chat_message(self, event):
        try:
            if self.user == event['user']:
                message = event['message_sender']
            else:
                message = event['message_receiver']

            if int(message) >= self.rsa_n_cookie_value:
                raise ValueError("Le message est trop grand pour être déchiffré")

            m = message_decrypt(int(message), self.rsa_d_cookie_value, self.rsa_n_cookie_value)
            decrypted_message = int_to_str(m)

            self.send(text_data=json.dumps({
                'user': str(event['user']),
                'message': decrypted_message,
                'time': str(event['time']),
            }))
            # print(f"Message envoyé dans la room {self.room_name}: {decrypted_message}")

        except ValueError as e:
            print(f"Erreur de taille du message : {e}")
        except Exception as e:
            print(f"Erreur lors de l'envoi du message : {e}")
