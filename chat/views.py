from django.shortcuts import render
from django.contrib.auth.models import User

from chat.models import Room


def index(request, user):
    user = User.objects.get(username=user)
    return render(request, 'base.html', {'rooms': user.user_rooms.all()})


def room(request, room_name):
    chat_room, created = Room.objects.get_or_create(name=room_name)
    return render(request, 'chat/index.html', {'room': chat_room, })


def login(request):
    return render(request, 'account/login.html')


def signup(request):
    return render(request, 'account/signup.html')
