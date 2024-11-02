from django.contrib import admin
from chat.models import Room, Message, PublicKey, UID

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(PublicKey)
admin.site.register(UID)