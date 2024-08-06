from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef
from django.shortcuts import render
from chat.models import Room, Message


def index(request):
    return render(request, 'index.html')


def chat(request):
    return render(request, 'rooms/index.html')


@login_required
def room(request, room_name):
    room = Room.objects.get(name=room_name)
    rooms = Room.objects.filter(user=request.user)
    last_message = Message.objects.filter(room=OuterRef('pk')).order_by('-timestamp')
    users_except_request_user = room.user.exclude(id=request.user.id)

    context = {
        'user': request.user,
        'users_except_request_user': users_except_request_user,
        'room_name': room_name,
        'rooms': rooms,
        'last_message': last_message
    }
    return render(request, 'rooms/index.html', context)


def add_contact(request):
    context = {

    }
    return render(request, 'rooms/contact.html', context)