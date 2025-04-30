from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv
import os
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

client_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_manager, requests_timeout=20)
print(f"Client ID: {SPOTIFY_CLIENT_ID[:5]}..., Secret: {SPOTIFY_CLIENT_SECRET[:5]}...")
print(sp.search(q="Beatles", type="artist", limit=1))