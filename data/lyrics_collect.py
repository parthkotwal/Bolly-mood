from dotenv import load_dotenv
import os
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
genius_token = os.getenv("GENIUS_ACCESS_TOKEN")

import lyricsgenius
import time
import pandas as pd

genius = lyricsgenius.Genius(genius_token)
genius.timeout = 20  # Increase timeout to handle slow responses
genius.sleep_time = 2  # Add delay to reduce request rate
genius.remove_section_headers = True
genius.excluded_terms = ["(Live)", "(Remix)"]

# Load artist names and existing dataset
artists = list(pd.read_csv("data/artistnames.csv")['Name'])
existing_data_file = "data/lyrics.csv"
try:
    existing_data = pd.read_csv(existing_data_file, encoding="utf-8")
    existing_titles = set(existing_data["title"].tolist())  # Track existing titles to avoid duplicates
    print(f"Loaded {len(existing_data)} existing songs.")
except FileNotFoundError:
    existing_data = pd.DataFrame(columns=["artist", "title", "lyrics"])
    existing_titles = set()
    print("No existing dataset found. Starting fresh.")

songs_data = []

# Retry logic for robust fetching
def fetch_artist_with_retry(artist_name, retries=3, wait_time=10):
    for attempt in range(retries):
        try:
            print(f"Fetching songs for {artist_name} (Attempt {attempt + 1}/{retries})...")
            artist_obj = genius.search_artist(artist_name, max_songs=40, sort="popularity")
            return artist_obj
        except Exception as e:
            print(f"Error fetching data for {artist_name} on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed to fetch data for {artist_name} after {retries} attempts.")
    return None

# Fetch songs for each artist
for artist in artists:
    artist_obj = fetch_artist_with_retry(artist, retries=3, wait_time=10)
    if artist_obj:
        for song in artist_obj.songs:
            if song.title not in existing_titles:
                songs_data.append({
                    "artist": artist,
                    "title": song.title,
                    "lyrics": song.lyrics
                })
                existing_titles.add(song.title) 
                time.sleep(1)
            else:
                print(f"Skipping duplicate song: {song.title}")

# Save the new data to the dataset
new_data = pd.DataFrame(songs_data)
combined_data = pd.concat([existing_data, new_data], ignore_index=True)
combined_data.to_csv(existing_data_file, index=False, encoding="utf-8")
print(f"Added {len(new_data)} new songs. Total dataset size: {len(combined_data)}")
print("Dataset saved!")