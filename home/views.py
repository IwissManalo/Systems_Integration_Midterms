from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render
import random
import string
import urllib.parse
import requests
from django.http import JsonResponse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_id = '0e7d735b06ac4782b4f0451ab70d5558'
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
        client_id = '0e7d735b06ac4782b4f0451ab70d5558'
        client_secret = 'b87c959964d348f58566a257f3e53afb'

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
                        # Fetch additional details for each artist (including followers count and top tracks)
                        for artist in data:
                            artist_id = artist.get('id')
                            artist_details_url = f"https://api.spotify.com/v1/artists/{artist_id}"
                            artist_details_response = requests.get(artist_details_url, headers=headers)
                            if artist_details_response.status_code == 200:
                                artist_details = artist_details_response.json()
                                artist['followers_count'] = artist_details.get('followers', {}).get('total', 0)
                                
                                # Fetch top tracks
                                top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
                                top_tracks_response = requests.get(top_tracks_url, headers=headers)
                                if top_tracks_response.status_code == 200:
                                    top_tracks_data = top_tracks_response.json().get('tracks', [])
                                    artist['top_tracks'] = [{'name': track['name'], 'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None} for track in top_tracks_data]
                                else:
                                    artist['top_tracks'] = []  # If unable to fetch top tracks, set to empty list
                            else:
                                artist['followers_count'] = 0
                                artist['top_tracks'] = []  # If unable to fetch top tracks, set to empty list
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
    
    

def search_song(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        if query:
            # Search for the song
            track_info = get_track_info(query)
            if track_info:
                search_results = [track_info]
                song_recommendations = get_recommendations(track_info['id'])
            else:
                search_results = None
                song_recommendations = None

            return render(request, 'home/music.html', {'search_results': search_results, 'song_recommendations': song_recommendations})

    return render(request, 'home/index.html')

def get_track_info(query):
    # Initialize Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id='0e7d735b06ac4782b4f0451ab70d5558', client_secret='b87c959964d348f58566a257f3e53afb')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Perform search for the song
    results = sp.search(q=query, limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        title = track['name']
        artist = track['artists'][0]['name']
        duration_ms = track['duration_ms']  # Duration in milliseconds
        duration = f"{int(duration_ms / 60000):02d}:{int((duration_ms / 1000) % 60):02d}"  # Convert duration to mm:ss format
        track_info = {
            'id': track['id'],
            'title': title,
            'artist': artist,
            'duration': duration,
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
        return track_info
    else:
        return None

def get_recommendations(track_id):
    # Initialize Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id='0e7d735b06ac4782b4f0451ab70d5558', client_secret='b87c959964d348f58566a257f3e53afb')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Get recommendations based on the track (linimit ko lang to 5)
    recommendations = sp.recommendations(seed_tracks=[track_id], limit=5)

    # Extract relevant information from the recommendations including image URLs
    song_recommendations = []
    for rec_track in recommendations['tracks']:
        duration_ms = rec_track['duration_ms']  # Duration in milliseconds
        duration = f"{int(duration_ms / 60000):02d}:{int((duration_ms / 1000) % 60):02d}"  # Convert duration to mm:ss format
        song_recommendations.append({
            'title': rec_track['name'],
            'artist': rec_track['artists'][0]['name'],
            'duration': duration,
            'image_url': rec_track['album']['images'][0]['url'] if rec_track['album']['images'] else None,
            'spotify_url': rec_track['external_urls']['spotify'] if 'spotify' in rec_track['external_urls'] else None
        })

    return song_recommendations