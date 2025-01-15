import requests
import pandas as pd
import time
from typing import List, Dict, Any

def get_songs_from_search(artist_id: int = 1186384) -> List[Dict[str, Any]]:
    """
    Fetch songs for KK (IND) using the artist ID from the Genius search API
    """
    base_url = "https://genius.com/api/artists/1186384/songs"  # KK (IND)'s artist ID
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    songs_data = []
    page = 1
    per_page = 50
    
    while True:
        try:
            params = {
                'page': page,
                'per_page': per_page,
                'sort': 'popularity'
            }
            
            print(f"Fetching page {page}...")
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'response' not in data or 'songs' not in data['response']:
                print("No more songs found.")
                break
                
            songs = data['response']['songs']
            if not songs:
                break
                
            for song in songs:
                # Skip if it's not primarily KK's song
                if "KK (IND)" not in song.get('artist_names', ''):
                    continue
                    
                # Skip remixes and live versions
                if any(term in song.get('title', '').lower() for term in ['(live)', '(remix)']):
                    continue
                    
                songs_data.append({
                    'artist': "KK (IND)",
                    'title': song.get('title', ''),
                    'full_title': song.get('full_title', ''),
                    'release_date': song.get('release_date_for_display', ''),
                    'url': song.get('url', ''),
                    'path': song.get('path', '')
                })
                
            print(f"Found {len(songs)} songs on page {page}")
            page += 1
            time.sleep(1)  # Be nice to the API
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    return songs_data

def fetch_lyrics(url: str) -> str:
    """
    Fetch lyrics for a given song URL
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # The lyrics are typically available in the API response at a different endpoint
        lyrics_url = f"https://genius.com/api{url.replace('https://genius.com', '')}"
        lyrics_response = requests.get(lyrics_url, headers=headers)
        lyrics_data = lyrics_response.json()
        
        if 'response' in lyrics_data and 'lyrics' in lyrics_data['response']:
            return lyrics_data['response']['lyrics']['plain']
        return "Lyrics not found"
        
    except Exception as e:
        print(f"Error fetching lyrics for {url}: {e}")
        return "Error fetching lyrics"

def main():
    existing_data_file = "data/lyrics.csv"
    
    # Load existing data
    try:
        existing_data = pd.read_csv(existing_data_file, encoding="utf-8")
        existing_titles = set(existing_data["title"].tolist())
        print(f"Loaded {len(existing_data)} existing songs.")
    except FileNotFoundError:
        existing_data = pd.DataFrame(columns=["artist", "title", "full_title", "release_date", "lyrics", "url"])
        existing_titles = set()
        print("No existing dataset found. Starting fresh.")
    
    # Get songs data
    songs_data = get_songs_from_search()
    
    if songs_data:
        # Filter out existing songs
        new_songs = [song for song in songs_data if song['title'] not in existing_titles]
        print(f"\nFound {len(new_songs)} new songs to process")
        
        # Fetch lyrics for new songs
        for song in new_songs:
            print(f"Fetching lyrics for: {song['title']}")
            song['lyrics'] = fetch_lyrics(song['url'])
            time.sleep(1)  # Be nice to the API
        
        # Create new dataframe and combine with existing data
        new_data = pd.DataFrame(new_songs)
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        
        # Save updated dataset
        combined_data.to_csv(existing_data_file, index=False, encoding="utf-8")
        print(f"\nAdded {len(new_songs)} new songs. Total dataset size: {len(combined_data)}")
        print("Dataset saved!")
    else:
        print("No songs found.")

if __name__ == "__main__":
    main()