from datetime import datetime
from django.shortcuts import render

def index(request):
    return render(request, 'base.html')

def login(request):
    return render(request, 'account/login.html')
def signup(request):
    return render(request, 'account/signup.html')
def chat(request):
    return render(request, 'chat/index.html')
