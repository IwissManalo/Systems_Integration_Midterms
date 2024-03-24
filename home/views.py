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

def artist(request):
    if request.method == 'GET':
        artist_name = request.GET.get('artist_name', '')

        if not artist_name:
            return render(request, 'home/artist.html', {'error': 'Please provide an artist name'})

        auth_url = 'https://accounts.spotify.com/api/token'
        client_id = 'ebfd357c105547999b9ca91002ef281f'
        client_secret = '206c1b048f344870bc05adb5049872cd'

        response = requests.post(
            auth_url,
            {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
            }
        )

        if response.status_code == 200:
            access_token = response.json().get('access_token')

            if access_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                }

                api_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=10"

                response = requests.get(api_url, headers=headers)

                if response.status_code == 200:
                    data = response.json().get('artists', {}).get('items', [])

                    if data:
                        # Fetch additional details for each artist (including followers count)
                        for artist in data:
                            artist_id = artist.get('id')
                            artist_details_url = f"https://api.spotify.com/v1/artists/{artist_id}"
                            artist_details_response = requests.get(artist_details_url, headers=headers)
                            if artist_details_response.status_code == 200:
                                artist_details = artist_details_response.json()
                                artist['followers_count'] = artist_details.get('followers', {}).get('total', 0)
                        return render(request, 'home/artist.html', {'data': data})
                    else:
                        return render(request, 'home/artist.html', {'error': 'No matching artists found'})
                else:
                    return render(request, 'home/artist.html', {'error': 'Failed to fetch artist data'})
            else:
                return render(request, 'home/artist.html', {'error': 'Failed to get access token'})
        else:
            return render(request, 'home/artist.html', {'error': 'Failed to authenticate with Spotify API'})
    else:
        return render(request, 'home/artist.html', {'error': 'Invalid request method'})
