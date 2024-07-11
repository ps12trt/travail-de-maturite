from django.urls import path
from .views import index, room, login, signup

urlpatterns = [
    path('', index, name="chat-index"),
    path('login/', login, name="login"),
    path('signup/', signup, name="signup"),
    path('<str:room_name>/', room, name="chat-room")
]
