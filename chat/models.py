from django.contrib.auth.models import User
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=128)
    user = models.ManyToManyField(to=User, blank=True, related_name='user_rooms')
    online = models.ManyToManyField(to=User, blank=True, related_name='online_rooms')

    def create_room(self, name):
        self.name = name
        self.save()

    def online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        users = ', '.join([user.get_username() for user in self.user.all()])
        return f'{self.name} ({users}): ({self.online_count()})'


class Message(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    content = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[{self.timestamp}], {self.room.name} ({self.user.username}): {self.content}'


class UID(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=36)

    def __str__(self):
        return f'User: {self.user.username}, [{self.uid}]'


class PublicKey(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    key = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'User: {self.user.username}, [{self.timestamp}], {self.key}'
