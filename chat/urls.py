from django.urls import path
from .views import index, room

urlpatterns = [
    path('', index, name="chat-index"),
    path('<str:room_name>/', room, name="chat-room")
]
