from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render
import random
import string
import urllib.parse
import requests
from django.http import JsonResponse

client_id = 'ebfd357c105547999b9ca91002ef281f'
redirect_uri = 'http://localhost:8888/callback'

def home(request):
    return render(request, 'home/index.html')

def music(request):
    return render(request, 'home/music.html')

def artist(request):
    return render(request, 'home/artist.html')

def genre(request):
    return render(request, 'home/genre.html')


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def login(request):
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email'
    query_params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri,
        'state': state
    }
    redirect_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(query_params)
    return redirect(redirect_url)
