from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from chat.models import Room, Message


def index(request):
    return render(request, 'base.html')


def get_most_recent_message(room):
    return Message.objects.filter(room=room).order_by('-timestamp').first()


@login_required
def room(request, room_name):
    room = Room.objects.get(name=room_name)
    rooms = Room.objects.filter(user=request.user)
    last_message = get_most_recent_message(room)
    users_except_request_user = room.user.exclude(id=request.user.id)

    context = {
        'user': request.user,
        'users_except_request_user': users_except_request_user,
        'room_name': room_name,
        'rooms': rooms,
        'last_message': last_message
    }
    return render(request, 'rooms/index.html', context)


def login(request):
    return render(request, 'account/login.html')


def signup(request):
    return render(request, 'account/signup.html')
