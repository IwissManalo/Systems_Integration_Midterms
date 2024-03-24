# # import spotipy  
# from spotipy.oauth2 import SpotifyOAuth

# CLIENT_ID = 'a31eccc0ff9d450f92622bc5c4bbc1b0'
# CLIENT_SECRET = '8c09393d6a06470085bef8a4a8132325'
# REDIRECT_URI = '//localhost:8000'
# SCOPE = "user-modify-playback-state"

# sp_oauth = SpotifyOAuth(
#     client_id=CLIENT_ID, 
#     client_secret=CLIENT_SECRET, 
#     redirect_uri=REDIRECT_URI, 
#     scope=SCOPE
#     )  
  
# access_token = sp_oauth.get_access_token()  
# refresh_token = sp_oauth.get_refresh_token()  

# print("Access token:", access_token)
# print("Refresh token:", refresh_token)

import requests

request = requests.post("https://accounts.spotify.com/api/token", 
                       headers={"Content-Type" : "application/x-www-form-urlencoded"},
                       params={"grant_type" : "client_credentials", 
                               "client_id" : "0e7d735b06ac4782b4f0451ab70d5558", 
                               "client_secret" : "b87c959964d348f58566a257f3e53afb"})


print(request.content);