from nltk.corpus import stopwords
from dotenv import load_dotenv
from google.cloud import translate_v3
from pathlib import Path
from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
import pandas as pd
import numpy as np
import re
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
        r"\(|\)",
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

def translate(lyrics: str, artist: str):
    language_scripts = {
        "as": r"[\u0980-\u09FF]+",  # Assamese
        "bn": r"[\u0980-\u09FF]+",  # Bengali
        "en": r"[a-zA-Z'’]+",       # English
        "gu": r"[\u0A80-\u0AFF]+",  # Gujarati
        "hi": r"[\u0900-\u097F]+",  # Hindi
        "kn": r"[\u0C80-\u0CFF]+",  # Kannada
        "ks": r"[\u0600-\u06FF]+",  # Kashmiri (Perso-Arabic script)
        "ml": r"[\u0D00-\u0D7F]+",  # Malayalam
        "mr": r"[\u0900-\u097F]+",  # Marathi
        "ne": r"[\u0900-\u097F]+",  # Nepali
        "or": r"[\u0B00-\u0B7F]+",  # Oriya (Odia)
        "pa": r"[\u0A00-\u0A7F]+",  # Punjabi
        "sa": r"[\u0900-\u097F]+",  # Sanskrit (Devanagari script)
        "sd": r"[\u0600-\u06FF]+",  # Sindhi (Arabic script)
        "ta": r"[\u0B80-\u0BFF]+",  # Tamil
        "te": r"[\u0C00-\u0C7F]+",  # Telugu
        "ur": r"[\u0600-\u06FF]+",  # Urdu (Perso-Arabic script)
    }

    # Remove all unnecessary characters and text from scraping
    lyrics = clean_lyrics(lyrics=lyrics, artist=artist)

    # Collect words from all detected languages
    words_to_translate = set()
    for lang, pattern in language_scripts.items():
        words_to_translate.update(re.findall(pattern, lyrics))

    # Include English and Romanized words
    words_to_translate.update(re.findall(r"[a-zA-Z'’]+", lyrics))

    # Convert set to list for batch API translation
    words_to_translate = list(words_to_translate)
    
    # Dictionary to store translations
    translations = {}

    if words_to_translate:
        try:
            response = client.translate_text(
                contents=words_to_translate,
                target_language_code="hi",
                parent=PARENT,
                mime_type="text/plain"
            )
            # Map original words to their translated versions
            for original, translated in zip(words_to_translate, response.translations):
                translations[original] = translated.translated_text
        except Exception as e:
            print(f"Translation error: {e}")

    # Replace words in lyrics with Hindi translations
    for word, translated in translations.items():
        lyrics = re.sub(rf'\b{re.escape(word)}\b', translated, lyrics)

    lyrics = lyrics.replace("'","")

    # Transliterate remaining words until there are none
    previous_lyrics = ""
    max_iterations = 10
    iteration = 0

    while lyrics != previous_lyrics and iteration < max_iterations:
        previous_lyrics = lyrics
        remaining_romanized = re.findall(r"[a-zA-Z'’]+", lyrics)
        if not remaining_romanized:
            break

        for word in remaining_romanized:
            transliterated_word = transliterate(word, ITRANS, DEVANAGARI)
            lyrics = re.sub(rf'\b{re.escape(word)}\b', transliterated_word, lyrics)

        iteration += 1

    return lyrics
   
# def clean_and_translate(lyrics: str, artist: str):
#     lyrics = clean_lyrics(lyrics, artist)
#     lyrics = translate(lyrics, artist)
#     return lyrics

specific_entry = df.iloc[393]
lyrics = specific_entry['raw_lyrics']
artist = specific_entry['artist']

print(f"Original: {lyrics}")
print(f"Translated: {translate(lyrics, artist)}")