import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import re
from dotenv import load_dotenv
import os
import rapidfuzz.fuzz as fuzz
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
import requests.exceptions
import time
import random
from tqdm import tqdm

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

client_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_manager, requests_timeout=20)

artists = list(pd.read_csv("data/metadata/artistnames.csv")['Name'].sort_values())
artists.insert(0,"AP Dhillon") #inserting at start because he has less number of songs, good for testing
existing_data_file = "data/metadata/spotify_metadata_new.csv"

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
    existing_songs = set()
    print("No existing dataset found. Starting fresh.")

completed_artists_file = "data/metadata/completed_artists.txt"
if os.path.exists(completed_artists_file):
    with open(completed_artists_file, "r", encoding="utf-8") as f:
        completed_artists = set(line.strip() for line in f)
else:
    completed_artists = set()


def safe_sp_call(func, *args, **kwargs):
    global sp, client_manager
    max_attempts = 5
    print(f"Calling {func.__name__}, args={args}, kwargs={kwargs}")

    for attempt in range(max_attempts):
        try:
            time.sleep(random.uniform(0.1, 0.5))
            return func(*args, **kwargs)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", "5"))
                print(f"Rate limited by Spotify. Sleeping for {retry_after} seconds...")
                time.sleep(retry_after + 2)
            elif e.http_status in [502, 503, 504]:
                sleep_time = random.uniform(2, 5)
                print(f"Spotify server error ({e.http_status}). Retrying after {sleep_time:.1f}s...")
                time.sleep(sleep_time)
            elif e.http_status in [401, 403]:
                print("Refreshing Spotify token...")
                client_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
                sp = spotipy.Spotify(client_credentials_manager=client_manager)
            else:
                raise
        except requests.exceptions.RequestException as e:
            print(f"SpotifyException in {func.__name__} with args={args}, kwargs={kwargs}")
            time.sleep(random.uniform(1, 3))

            if hasattr(e, 'response') and e.response is not None:
                print("RESPONSE BODY:", e.response.text)
            raise
    raise Exception(f"Max retries reached for {func.__name__}")

songs_data = []
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=1, max=8))
def fetch_artist_songs(artist_name: str) -> List[dict]:
    songs = []
    results = safe_sp_call(sp.search, q=f"artist:{artist_name}", type='artist', limit=1)
    if not results['artists']['items']:
        print(f"No Spotify artist found for {artist_name}")
        return songs
    
    artist_id = results['artists']['items'][0]['id']
    albums = []
    seen_albums = set()
    limit = 50
    offset = 0

    while True:
        album_results = safe_sp_call(sp.artist_albums, artist_id, album_type='album,single,compilation', limit=limit, offset=offset)
        albums_batch = album_results['items']
        if not albums_batch:
            break

        for album in albums_batch:
            if album['id'] not in seen_albums:
                albums.append(album)
                seen_albums.add(album['id'])

        if album_results['next']:
            offset += limit
        else:
            break

    print(f"Found {len(albums)} albums for {artist_name}")

    for album in tqdm(albums, desc=f"Fetching tracks for {artist_name}", leave=False):
        try:
            album_tracks = safe_sp_call(sp.album_tracks, album['id'])
            for track in album_tracks['items']:
                track_artists = [artist['name'].lower() for artist in track['artists']]
                artist_name_clean = re.sub(r'\W+', '', artist_name).lower()

                match_found = False
                for track_artist in track_artists:
                    track_artist_clean = re.sub(r'\W+', '', track_artist).lower()
                    if fuzz.ratio(artist_name_clean, track_artist_clean) > 60:
                        match_found = True
                        break

                if not match_found:
                    continue

                title = track['name']
                cleaned_title = re.sub(r'[^\w\s]', '', title).lower().strip()
                existing_clean_titles = {re.sub(r'[^\w\s]', '', t).lower().strip() for t in existing_songs}
                if cleaned_title in existing_clean_titles:
                    continue

                song_data = {
                    "spotify_id": track['id'],
                    "artist": artist_name,
                    "title": title,
                    "album": album['name'],
                    "release_date": album['release_date'],
                    "popularity": None, 
                    "acousticness": None,
                    "danceability": None,
                    "duration_ms": track['duration_ms'],
                    "energy": None,
                    "instrumentalness": None,
                    "liveness": None,
                    "loudness": None,
                    "speechiness": None,
                    "tempo": None,
                    "valence": None,
                }
                songs.append(song_data)
                
        except Exception as e:
            print(f"Failed to fetch tracks for album {album['name']}: {e}")
            continue

    return songs


def fetch_audio_features(song_ids: List[str]):
    feature_dict = {}
    batch_size = 50
    for i in range(0, len(song_ids), batch_size):
        batch = song_ids[i:i+batch_size]
        valid_ids = [sid for sid in batch if isinstance(sid, str) and len(sid) == 22]

        if not valid_ids:
            print(f"Skipping batch with invalid IDs: {batch}")
            continue

        try:
            print(f"Fetching audio features for batch: {valid_ids}")
            features = safe_sp_call(sp.audio_features, valid_ids)
            if features is None:
                print(f"No features returned for batch: {valid_ids}")
                continue

            time.sleep(random.uniform(0.5, 1.5))  # Be nice to the API
            for feat in features:
                if feat:
                    feature_dict[feat['id']] = {
                        "acousticness": feat['acousticness'],
                        "danceability": feat['danceability'],
                        "energy": feat['energy'],
                        "instrumentalness": feat['instrumentalness'],
                        "liveness": feat['liveness'],
                        "loudness": feat['loudness'],
                        "speechiness": feat['speechiness'],
                        "tempo": feat['tempo'],
                        "valence": feat['valence'],
                    }
        except Exception as e:
            print(f"Error fetching features for batch {valid_ids}: {e}")
    return feature_dict
       

# main loop
for artist in tqdm(artists, desc="Processing artists"):
    if artist in completed_artists:
        print(f"Skipping {artist}, already processed.")
        continue

    try:
        print(f"Fetching songs for {artist}...")
        new_songs = fetch_artist_songs(artist)
        if not new_songs:
            print(f"No new songs found for {artist}")
            with open(completed_artists_file, "a", encoding="utf-8") as f:
                f.write(artist + "\n")
            continue
        
        song_ids = [song['spotify_id'] for song in new_songs]
        audio_features = fetch_audio_features(song_ids)

        for song in new_songs:
            features = audio_features.get(song['spotify_id'], {})
            for key, value in features.items():
                song[key] = value

        new_df = pd.DataFrame(new_songs)
        updated_df = pd.concat([existing_data, new_df], ignore_index=True)
        updated_df.drop_duplicates(subset=["spotify_id"], inplace=True)
        updated_df.to_csv(existing_data_file, index=False, encoding="utf-8")
        existing_data = updated_df  # update in-memory existing_data

        # Mark artist as completed
        with open(completed_artists_file, "a", encoding="utf-8") as f:
            f.write(artist + "\n")
        print(f"Saved {len(new_songs)} songs for {artist}. Total songs now: {len(updated_df)}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {artist}: {e}")
    except RetryError as e:
        print(f"RetryError for {artist}: {e.last_attempt.exception()}")
    except Exception as e:
        print(f"Unexpected error for {artist}: {e}")

if songs_data:
    new_df = pd.DataFrame(songs_data)
    updated_df = pd.concat([existing_data, new_df], ignore_index=True)
    updated_df.to_csv(existing_data_file, index=False, encoding="utf-8")
    print(f"Saved {len(songs_data)} new songs. Total songs: {len(updated_df)}")
else:
    print("No new songs were added.")