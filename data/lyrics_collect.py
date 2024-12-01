from dotenv import load_dotenv
import os
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
genius_token = os.getenv("GENIUS_ACCESS_TOKEN")

import lyricsgenius
import json
import time
import pandas as pd

genius = lyricsgenius.Genius(genius_token)
genius.timeout = 10  
genius.sleep_time = 1 
genius.remove_section_headers = True 
genius.excluded_terms = ["(Live)", "(Remix)"] 

artists = list(pd.read_csv("data/artistnames.csv")['Name'])
songs_data = []

for artist in artists:
    print(f"Fetching songs for {artist}...")
    try:
        artist_obj = genius.search_artist(artist, max_songs=40, sort="popularity")
        for song in artist_obj.songs:
            songs_data.append({
                "artist": artist,
                "title": song.title,
                "lyrics": song.lyrics
            })
            time.sleep(1)

    except Exception as e:
        print(f"Error fetching data for {artist}: {e}")

df = pd.DataFrame(songs_data)
df.to_csv("data/bollywood_songs_lyrics.csv", index=False, encoding="utf-8")
print("Dataset saved!")

# stopped at AR Rahman