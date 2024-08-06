from django.urls import path
from .views import index, room, chat, add_contact

urlpatterns = [
    path('', index, name="chat-index"),
    path('chat/<str:room_name>/', room, name="chat-room"),
    path('chat/', chat, name="chat"),
    path('add-contact/', add_contact, name="add-contact")
]
