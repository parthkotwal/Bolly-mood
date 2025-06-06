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

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=1, max=8))
def search_song(genius_title:str, genius_artist:str):
    try:
        query = f"title:{genius_title} artist:{genius_artist}"
        results = sp.search(q=query, type="track", limit=5)
        if not results['tracks']['items']:
            query = f"{genius_title} {genius_artist}"
            results = sp.search(q=query, type="track", limit=5)

        for track in results['tracks']['items']:
            spotify_title = track["name"]
            spotify_artists = [a["name"] for a in track["artists"]]

            if match_artist(genius_artist, spotify_artists) and match_titles(genius_title, spotify_title):
                print(f"'{track['name']}' by '{', '.join(spotify_artists)}' added to dataset.")
                return {
                    "spotify_id":track["id"],
                    "title":genius_title,
                    "artist":", ".join(spotify_artists),
                    "album": track["album"]["name"],
                    "release_date": track["album"]["release_date"],
                    "popularity": track["popularity"]
                }
    
    except requests.exceptions.ReadTimeout:
        print(f"Timeout error for '{genius_title}' by '{genius_artist}'")
        return None
    
    return None
    
def get_audio_features(spotify_id:str):
    features = sp.audio_features([spotify_id])
    if features and features[0]:
        features = features[0]
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

def clean_title(title:str):
    title = re.sub(r"\(.*?\)|\[.*?\]|\".*?\"", "", title)
    title = re.sub(r"[-–]?\s?(Lyrics|Lyric Video|Official Video|Song)$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^From\s+", "", title, flags=re.IGNORECASE)
    title = re.sub(r'[\u0900-\u097F]+', '', title)
    return title.strip().lower()

def match_titles(genius_title:str, spotify_title:str, threshold=70):
    genius_title = clean_title(genius_title)
    spotify_title = clean_title(spotify_title)

    similarity = fuzz.partial_ratio(genius_title, spotify_title)
    return similarity >= threshold

def match_artist(genius_artist:str, spotify_artists:List[str]):
    genius_artist = genius_artist.lower()

    for artist in spotify_artists:
        similarity = fuzz.partial_ratio(genius_artist, artist.lower())
        if similarity >= 80:
            return True
        
    return False

# lyrics_data = pd.read_csv("data/lyrics/lyrics_cleaned_labelled_gcp.csv")
# # spotify_data = lyrics_data.apply(lambda row: search_song(row['title'], row['artist']), axis=1)
# # spotify_data = spotify_data.dropna().apply(pd.Series)
# spotify_data = pd.read_csv("data/metadata/spotify_metadata.csv")

# missing_songs = lyrics_data[~lyrics_data['title'].isin(spotify_data['title'])]
# retrieved_metadata = missing_songs.apply(lambda row: search_song(row['title'], row['artist']), axis=1)
# retrieved_metadata = retrieved_metadata.dropna().apply(pd.Series)

# spotify_data = pd.concat([spotify_data, retrieved_metadata], ignore_index=True)

# print(f"After re-matching, total matched songs: {len(retrieved_metadata)}")
# print(retrieved_metadata)

# spotify_data.to_csv("data/metadata/spotify_metadata.csv", index=False)
# missing_songs.to_csv("data/metadata/missing_songs.csv", index=False)

# # missing_songs.to_csv("data/metadata/missing_songs.csv", index=False)
# print("Metadata extraction completed successfully!")

spotify_data = pd.read_csv("data/metadata/spotify_metadata.csv")
missing_songs = pd.read_csv("data/metadata/missing_songs.csv")

retrieved_metadata = missing_songs.apply(lambda row: search_song(row['title'], row['artist']), axis=1)
retrieved_metadata = retrieved_metadata.dropna().apply(pd.Series)

spotify_data = pd.concat([spotify_data, retrieved_metadata], ignore_index=True)

matched_titles_artists = set(zip(retrieved_metadata['title'], retrieved_metadata['artist']))
missing_songs = missing_songs[~missing_songs.apply(lambda row: (row['title'], row['artist']) in matched_titles_artists, axis=1)]

spotify_data.to_csv("data/metadata/spotify_metadata.csv", index=False)
missing_songs.to_csv("data/metadata/missing_songs.csv", index=False)

print(f"After re-matching, total matched songs: {len(retrieved_metadata)}")
print(f"Remaining missing songs: {len(missing_songs)}")