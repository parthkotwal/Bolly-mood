import pandas as pd
import numpy as np
import re
from nltk.corpus import stopwords
from dotenv import load_dotenv
from google.cloud import translate_v3
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
GCP_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
PARENT = f"projects/{PROJECT_ID}/locations/global"

# Initialize the Translation client
client = translate_v3.TranslationServiceClient.from_service_account_file(GCP_CREDENTIALS)

df = pd.read_csv('data/lyrics/lyrics.csv')
df.columns = ['artist', 'title','raw_lyrics']

def detect_script(lyrics:str) -> str:
    devanagari_pattern = r'[\u0900-\u097F]'
    gurmukhi_pattern = r'[\u0A00-\u0A7F]'
    tamil_pattern = r'[\u0B80-\u0BFF]'
    bengali_pattern = r'[\u0980-\u09FF]'
    
    if re.search(devanagari_pattern, lyrics):
        return 'devanagari'
    elif re.search(gurmukhi_pattern, lyrics):
        return 'gurmukhi'
    elif re.search(tamil_pattern, lyrics):
        return 'tamil'
    elif re.search(bengali_pattern, lyrics):
        return 'bengali'
    else:
        return 'roman'
    
# def detect_and_translate_mixed_script(lyrics: str) -> str:
#     english_words = re.findall(r'[a-zA-Z][a-zA-Z\'’]*', lyrics)
    
#     if not english_words:
#         return lyrics
    
#     translations = {}
#     for word in english_words:
#         try:
#             response = client.translate_text(
#             contents=[word, target_language_code="hi"
#             )["translatedText"]
#             translations[word] = translated_text

#     try:
#         response = client.translate_text(
#             contents=[lyrics],
#             target_language_code="hi",
#             parent=PARENT,
#             mime_type="text/plain"
#         )
#         return response.translations[0].translated_text
#     except Exception as e:
#         print(f"Translation error: {e}")
#         return lyrics
    
#     # Replace English words with their translations
#     for word, translated in translations.items():
#         lyrics = re.sub(rf'\b{re.escape(word)}\b', translated, lyrics)
    
#     return lyrics
    
def translate_to_hindi(lyrics:str):
    try:
        response = client.translate_text(
            contents=[lyrics],
            target_language_code="hi",
            parent=PARENT,
            mime_type="text/plain"
        )
        return response.translations[0].translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return lyrics
    
def clean_lyrics(lyrics: str, artist: str):
    # Convert lyrics to lowercase for consistent matching
    lyrics = lyrics.lower()
    
    # Split the artist name into first and last names
    artist_parts = artist.split()
    artist_first_name = artist_parts[0] if len(artist_parts) > 0 else ""
    artist_last_name = artist_parts[1] if len(artist_parts) > 1 else ""
    
    # Define the patterns to remove
    patterns = [
        r'\b(embed|you might also like|related songs|other songs you might like|advertisement|promo)\b',  # Various unwanted phrases
        r'\[.*?\]',  # Any text within square brackets
        r'http[s]?://\S+',  # URLs
        r'--+',  # Long dashes
        r'^\s*$',  # Empty lines
        r"^\d+\s*contributor.*?lyrics",  # Contributor section
        r'embed',
        r'you might also like',
        rf'see\s+{artist_first_name.lower()}\s*{artist_last_name.lower()}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like',
        rf'see\s+{artist_first_name.lower()}\s*liveget\s*tickets\s*as\s*low\s*as\s*\+\s*you\s*might\s*also\s*like',
        rf'see\s+{artist_last_name.lower()}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like',
        rf'lyrics\s*source\s+{artist_first_name.lower()}\s*{artist_last_name.lower()}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like',
        '\d+see\s+udit\s+narayan\s+liveget\s+tickets\s+as\s+low\s+as\s+\d+'
    ]
    
    # Loop through each pattern and remove it from the lyrics
    for pattern in patterns:
        lyrics = re.sub(pattern, '', lyrics, flags=re.IGNORECASE)
    
    # Clean up extra spaces that might have been left behind
    lyrics = re.sub(r'\s+', ' ', lyrics).strip()

    return lyrics

def clean_and_standardize(lyrics: str, artist: str):
    lyrics = clean_lyrics(lyrics, artist)
    lyrics = translate_to_hindi(lyrics)
    return lyrics

row_index = 2
specific_entry = df.iloc[row_index]
lyrics = specific_entry['raw_lyrics']
artist = specific_entry['artist']

english_words = re.findall(r"[a-zA-Z'’]+(?: [a-zA-Z'’]+)*", clean_lyrics(lyrics, artist))
try:
    english_words.remove("'")
except ValueError as v:
    english_words
    
print('phone')