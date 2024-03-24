# home/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('music/', views.music, name='music'),  # Add URL pattern for Music
    path('search/', views.search_song, name='search_song'), 
    path('artist/', views.artist, name='artist'),  # Add URL pattern for Artist
    path('genre/', views.genre, name='genre'),  # Add URL pattern for Genre
    
]
