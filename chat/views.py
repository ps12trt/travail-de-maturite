import string
import uuid

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from chat.models import Room, PublicKey, UID
from chat.rsa import *


def index(request):
    if request.user.is_authenticated:
        try:
            PublicKey.objects.get(user=request.user)
        except PublicKey.DoesNotExist:
            return redirect(create_keys)

        if 'rsa_priv_key_n' or 'rsa_priv_key_d' not in request.COOKIES:
            return redirect(privkey_login)

    return render(request, 'index.html')


@login_required
def room(request, room_name=""):
    if 'rsa_priv_key_n' not in request.COOKIES:
        return redirect(privkey_login)

    if not room_name == "":
        room = get_object_or_404(Room, name=room_name)
        users_except_request_user = room.user.exclude(id=request.user.id)

        if request.user not in room.user.all():
            return HttpResponseForbidden("<h1>Vous n'êtes pas autorisé à accéder à cette salle.</h1>")

        rsa_r_pubkey_pem = PublicKey.objects.get(user=room.user.exclude(id=request.user.id).first())
        rsa_s_pubkey_pem = PublicKey.objects.get(user=request.user)
        n_r, e_r = pem_to_publickey(rsa_r_pubkey_pem.key)
        n_s, e_s = pem_to_publickey(rsa_s_pubkey_pem.key)
    else:
        room = None
        users_except_request_user = None
        n_r, n_s, e_r, e_s = None, None, None, None

    rooms = Room.objects.filter(user=request.user)

    context = {
        'room_name': room_name,
        'rooms': rooms,
        'user': request.user,
        'users_except_request_user': users_except_request_user,
    }
    response = render(request, 'rooms/index.html', context)
    if n_r and n_s and e_r and e_s:
        response.set_cookie('rsa_pub_key_nr', n_r)
        response.set_cookie('rsa_pub_key_ns', n_s)
        response.set_cookie('rsa_pub_key_er', e_r)
        response.set_cookie('rsa_pub_key_es', e_s)
    return response


def create_numbers():
    p = random_prime_number(308)
    q = random_prime_number(308)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = create_public_exponent(phi)
    d = create_private_exponent(e, phi)
    return n, e, d, p, q


@login_required
def create_keys(request):
    try:
        PublicKey.objects.get(user=request.user).key
    except PublicKey.DoesNotExist:
        random_name = uuid.uuid4()
        n, e, d, p, q = create_numbers()
        privatekey = privatekey_to_pem(n, e, d, p, q)
        publickey = publickey_to_pem(n, e)

        PublicKey.objects.create(user=request.user, key=publickey)
        UID.objects.create(user=request.user, uid=random_name)
        request.session['privatekey'] = privatekey

        context = {
            'publickey': publickey,
            'privatekey': privatekey,
            'uid': random_name
        }
        return render(request, 'registration/createkeys.html', context)
    return render(request, 'registration/createkeys.html')


def regenerate_keys(request):
    PublicKey.objects.get(user=request.user).delete()
    n, e, d, p, q = create_numbers()
    privatekey = privatekey_to_pem(n, e, d, p, q)
    publickey = publickey_to_pem(n, e)
    PublicKey.objects.create(user=request.user, key=publickey)
    request.session['privatekey'] = privatekey

    context = {
        'publickey': publickey,
        'privatekey': privatekey,
    }
    return render(request, 'registration/createkeys.html', context)


def privkey_login(request):
    if request.method == 'POST':
        if 'pem_file' in request.FILES:
            pem_file = request.FILES['pem_file']
            pem_content = pem_file.read().decode('utf-8')

            n, d = extract_from_pem(pem_content)

            response = render(request, "registration/privkey_login.html")
            if n and d:
                response = redirect('chat')
                response.set_cookie('rsa_priv_key_n', n)
                response.set_cookie('rsa_priv_key_d', d)
            return response
        else:
            return HttpResponse("Aucun fichier n'a été soumis", status=400)

    return render(request, "registration/privkey_login.html")


def extract_from_pem(pem):
    n, d = pem_to_privatekey(pem)[1], pem_to_privatekey(pem)[3]
    return n, d


def random_room_name():
    letters = string.ascii_lowercase
    numbers = string.digits
    return ''.join(random.choice(letters + numbers) for i in range(20))


@login_required
def add_contact(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        uid_user = UID.objects.get(uid=uid).user

        random_name = random_room_name()
        new_room = Room.objects.create(name=random_name)
        new_room.user.add(request.user)
        new_room.user.add(uid_user)

        context = {
            'uid': uid,
        }

        return render(request, 'rooms/contact.html', context)

    return render(request, 'rooms/contact.html')


@login_required
def profile(request):
    publickey = PublicKey.objects.get(user=request.user).key
    uid = UID.objects.get(user=request.user).uid

    context = {
        'uid': uid,
        'publickey': publickey,
    }
    return render(request, "registration/profile.html", context)


@login_required
def download_key_pem(request):
    publickey = PublicKey.objects.get(user=request.user).key
    filename = f"{request.user}-publickey.pem"

    if publickey:
        response = HttpResponse(publickey, content_type='application/x-pem-file')
        response['Content-Disposition'] = f'attachment; filename="{str(filename)}'
        return response
    else:
        return HttpResponse("Aucune clée trouvée", status=404)


@login_required
def download_privkey_pem(request):
    privatekey = request.session.get('privatekey')
    filename = f"{request.user}-privatekey.pem"

    if privatekey:
        response = HttpResponse(privatekey, content_type='application/x-pem-file')
        response['Content-Disposition'] = f'attachment; filename="{str(filename)}"'
        return response
    else:
        return HttpResponse("Aucune clée trouvée", status=404)


def logout_cookies(request):
    logout(request)
    response = redirect('login')
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    return response
