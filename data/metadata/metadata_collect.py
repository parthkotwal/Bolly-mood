import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from fuzzywuzzy import fuzz
import re
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

client_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_manager)

def search_song(genius_title:str, genius_artist:str):
    query = f"track:{genius_title} artist:{genius_artist}"
    results = sp.search(q=query, type="track", limit=5)

    for track in results['tracks']['items']:
        spotify_title = track["name"]
        spotify_artists = [a["name"] for a in track["artists"]]

        if match_artist(genius_artist, spotify_artists) and match_titles(genius_title, spotify_title):
            return {
            "spotify_id":track["id"],
            "title":track["name"],
            "artist":", ".join(spotify_artists),
            "album": track["album"]["name"],
            "release_date": track["album"]["release_date"],
            "popularity": track["popularity"]
            }

    return None
    
def get_audio_features(spotify_id:str):
    features = sp.audio_features([spotify_id])[0]

    if features:
        return {
            "acousticness":features["acousticness"],
            "danceability":features["danceability"],
            "duration_ms":features["duration_ms"],
            "energy":features["energy"],
            "instrumentalness":features["instrumentalness"],
            "liveness":features["liveness"],
            "loudness":features["loudness"],
            "speechiness":features["speechiness"],
            "tempo":features["tempo"],
            "valence":features["valence"]
        }
    
    return None

def clean_title(title):
    title = re.sub(r"\(.*?\)|\[.*?\]|\".*?\"", "", title)
    title = re.sub(r'[\u0900-\u097F]+', '', title)
    title = title.strip()

    if " - " in title:
        title = title.split(" - ")[-1].strip()

    return title.lower()

def match_titles(genius_title, spotify_title, threshold=80):
    genius_title = clean_title(genius_title)
    spotify_title = clean_title(spotify_title)

    similarity = fuzz.ratio(genius_title, spotify_title)
    return similarity >= threshold

def match_artist(genius_artists, spotify_artists):
    genius_artist = genius_artist.lower()
    spotify_artists = [a.lower() for a in spotify_artists]

    for artist in spotify_artists:
        if genius_artist in artist or artist in genius_artist:
            return True
        
    return False