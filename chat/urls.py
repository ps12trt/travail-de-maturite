from django.urls import path
from .views import index, room, add_contact, create_keys, profile, download_key_pem, privkey_login, download_privkey_pem, regenerate_keys

urlpatterns = [
    path('', index, name="chat-index"),
    path('chat/<str:room_name>/', room, name="chat-room"),
    path('chat/', room, name="chat"),
    path('profile/', profile, name="profile"),
    path('add-contact/', add_contact, name="add-contact"),
    path('create-keys/', create_keys, name="create-keys"),
    path('pem/pub/download/', download_key_pem, name="pub_download_pem"),
    path('pem/priv/download/', download_privkey_pem, name="priv_download_pem"),
    path('regen-keys', regenerate_keys, name="regen_key"),
    path('login-rsa/', privkey_login, name="privkey-login"),
]
