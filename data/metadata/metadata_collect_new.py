import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import rapidfuzz.fuzz as fuzz
import pandas as pd
import re
from dotenv import load_dotenv
import os
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
import requests.exceptions

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

client_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_manager, requests_timeout=20)

artists = list(pd.read_csv("data/metadata/artistnames.csv")['Name'])
existing_data_file = "data/metadata/spotify_metadata.csv"
try:
    existing_data = pd.read_csv(existing_data_file, encoding="utf-8")
    existing_songs = set(existing_data['title'].tolist())
    print(f"Loaded {len(existing_data)} existing songs.")
except FileNotFoundError:
    existing_data = pd.DataFrame(columns=[
        "spotify_id", 
        "artist", 
        "title", 
        "album",
        "release_date",
        "popularity",
        "acousticness",
        "danceability",
        "duration_ms",
        "energy",
        "instrumentalness",
        "liveness",
        "loudness",
        "speechiness",
        "tempo",
        "valence"
        ])
    existing_titles = set()
    print("No existing dataset found. Starting fresh.")

songs_data = []
def fetch_artist()