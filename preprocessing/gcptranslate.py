import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI, GURMUKHI, TAMIL, BENGALI
from google.cloud import translate_v3
import os
from dotenv import load_dotenv
from google.cloud import translate_v3
from pathlib import Path

# Load environment variables from .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    
def detect_script(lyrics:str) -> str:
    devanagari_pattern = r'[\u0900-\u097F]'  # Devanagari
    romanized_pattern = r'[a-zA-Z]'  # Romanized characters
    tamil_pattern = r'[\u0B80-\u0BFF]'  # Tamil
    bengali_pattern = r'[\u0980-\u09FF]'  # Bengali
    gurmukhi_pattern = r'[\u0A00-\u0A7F]'  # Gurmukhi

    devanagari_count = len(re.findall(devanagari_pattern, lyrics))
    romanized_count = len(re.findall(romanized_pattern, lyrics))
    tamil_count = len(re.findall(tamil_pattern, lyrics))
    bengali_count = len(re.findall(bengali_pattern, lyrics))
    gurmukhi_count = len(re.findall(gurmukhi_pattern, lyrics))

    # Determine the dominant script
    counts = {
        'devanagari': devanagari_count,
        'roman': romanized_count,
        'tamil': tamil_count,
        'bengali': bengali_count,
        'gurmukhi': gurmukhi_count,
    }

    dominant_script = max(counts, key=counts.get)
    return dominant_script if counts[dominant_script] > 0 else 'unknown'

def clean_lyrics(lyrics:str, artist:str) -> str:
    lyrics = lyrics.lower()
    artist_parts = artist.split()
    artist_first_name = artist_parts[0] if len(artist_parts) > 0 else ""
    artist_last_name = artist_parts[1] if len(artist_parts) > 1 else ""

    patterns = [
        r'\b(embed|you might also like|related songs|other songs you might like|advertisement|promo|Embed|1Embed|2Embed)\b',
        r'\[.*?\]',  # Any text within square brackets
        r'http[s]?://\S+',  # URLs
        r'--+',  # Long dashes or similar
        r'^\s*$',  # Empty lines or lines containing only spaces
        r"^\d+\s*contributor.*?lyrics",  # n ContributorsSongName Lyrics
        r'embed',
        rf'see\s+{artist_first_name.lower()}\s*{artist_last_name.lower()}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like',
        rf'see\s+{artist_first_name.lower()}\s*liveget\s*tickets\s*as\s*low\s*as\s*\+\s*you\s*might\s*also\s*like',
        rf'see\s+{artist_last_name.lower()}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like',
        rf'lyrics\s*source\s+{artist_first_name.lower()}\s*{artist_last_name.lower()}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like',
        '\d+see\s+udit\s+narayan\s+liveget\s+tickets\s+as\s+low\s+as\s+\d+'
    ]
    for pattern in patterns:
        lyrics = re.sub(pattern, '', lyrics, flags=re.IGNORECASE)

    lyrics = re.sub(r'\s+', ' ', lyrics).strip()
    return lyrics

def translate_to_hindi(lyrics:str, source_lang:str=None) -> str:
    client = translate_v3.TranslationServiceClient()
    parent = f"projects/{PROJECT_ID}/locations/global"

    try:
        if source_lang:
            response = client.translate_text(
                contents=[lyrics],
                source_language_code=source_lang,
                target_language_code="hi",
                parent=parent,
                mime_type="text/plain"
            )
            return response.translations[0].translated_text
        else:
            response = client.translate_text(
                contents=[lyrics],
                target_language_code="hi",
                parent=parent,
                mime_type="text/plain"
            )
            return response.translations[0].translated_text
        
    except Exception as e:
        print(f"Translation failed for lyrics: {lyrics[:30]}... Error: {e}")
        return lyrics

def clean_and_translate(lyrics:str, artist:str, max_iter:int=5):
    iterations = 0
    lyrics = clean_lyrics(lyrics, artist)  # Initial cleaning step

    while iterations < max_iter:
        script = detect_script(lyrics)
        
        if script == "devanagari":
            non_devanagari_pattern = r'[^\s\u0900-\u097F]'  # Non-Devanagari characters
            if not re.search(non_devanagari_pattern, lyrics):
                break
        
        elif script == "roman":
            try:
                lyrics = translate_to_hindi(lyrics)  # Assume Romanized text as English-like
            except Exception as e:
                print(f"Translation error: {e}")
                return None

        elif script in ['tamil', 'bengali', 'gurmukhi']:
            try:
                source_lang = {
                    'tamil': 'ta',
                    'bengali': 'bn',
                    'gurmukhi': 'pa',  # Punjabi
                }.get(script, None)
                lyrics = translate_to_hindi(lyrics, source_lang=source_lang)
            except Exception as e:
                print(f"Translation error: {e}")
                return None
        else:
            # If script is unknown, log and skip processing
            try:
                # Use the translation API for mixed or unknown content
                lyrics = translate_to_hindi(lyrics, source_lang="auto")  # Automatically detect source language
            except Exception as e:
                print(f"Translation error: {e}")
                return None
        
        lyrics = clean_lyrics(lyrics, artist)
        iterations += 1

    lyrics = re.sub(r'[^\s\u0900-\u097F]', '', lyrics).strip()
    return lyrics

df = pd.read_csv('data/lyrics/lyrics.csv')
print(clean_and_translate("This is a test गीत with mixed scripts.",'Aastha Gill'))