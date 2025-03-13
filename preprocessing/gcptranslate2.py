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

# Define the patterns to remove
STATIC_CLEAN_PATTERNS = [re.compile(p, flags=re.IGNORECASE) for p in [
    r'\b(embed|you might also like|related songs|other songs you might like|advertisement|promo)\b',  # Various unwanted phrases
    r'\[.*?\]',  # Any text within square brackets
    r'http[s]?://\S+',  # URLs
    r'--+',  # Long dashes
    r'^\s*$',  # Empty lines
    r"^\d+\s*contributor.*?lyrics",  # Contributor section
    r'embed',
    r"\(|\)",
    r"1",
    r'you might also like',
    r'\*',
    r"\$'?[\d,]+'?",
    r"(?<!\.)\.(?!\.)",
    r'(?<!।)।(?!।)',
    r'x2',
    r'x3',
    r'x4',
    r'x5',
    r'x6',
    r'x7',
    r'x8',
    '\d+see\s+udit\s+narayan\s+liveget\s+tickets\s+as\s+low\s+as\s+\d+'
]]
INSTRUMENTAL_PATTERN = re.compile(r"this\s+song\s+is\s+an\s+instrumentalembed", flags=re.IGNORECASE)

# Detect the script of the lyrics (ex: Devanagari, Gurmukhi etc.)
def detect_script(lyrics:str) -> str:
    script_ranges = {
        "hi": (0x0900, 0x097F),  # Devanagari
        "pa": (0x0A00, 0x0A7F),  # Gurmukhi
        "bn": (0x0980, 0x09FF),  # Bengali
        "gu": (0x0A80, 0x0AFF),  # Gujarati
        "ta": (0x0B80, 0x0BFF),  # Tamil
        "te": (0x0C00, 0x0C7F),  # Telugu
        "kn": (0x0C80, 0x0CFF),  # Kannada
        "ml": (0x0D00, 0x0D7F),  # Malayalam
        "or": (0x0B00, 0x0B7F),  # Oriya
        "en": (0x0020, 0x007E),  # English
        "ar": (0x0600, 0x06FF),  # Arabic/Urdu
    }
    
    char_counts = {script: 0 for script in script_ranges}
    for char in lyrics:
        code = ord(char)
        for script, (start, end) in script_ranges.items():
            if start <= code <= end:
                char_counts[script] += 1
                break
    
    # Return the script with the most characters, or None if no matches
    return max(char_counts, key=char_counts.get) if any(char_counts.values()) else None

# Dynamic patterns function
def dynamic_patterns(artist: str):
    artist_parts = artist.split()
    artist_first_name = artist_parts[0].lower() if artist_parts else ""
    artist_last_name = artist_parts[1].lower() if len(artist_parts) > 1 else ""

    return [re.compile(p.format(first=artist_first_name, last=artist_last_name), flags=re.IGNORECASE) for p in [
        r'see\s+{first}\s*{last}\s*liveget\s*tickets\s*as\s*low\s*as',
        r'see\s+{first}\s*{last}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like',
        r'see\s+{first}\s*liveget\s*tickets\s*as\s*low\s*as\s*\+\s*you\s*might\s*also\s*like',
        r'see\s+{last}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like',
        r'lyrics\s*source\s+{first}\s*{last}\s*liveget\s*tickets\s*as\s*low\s*as\s*\d+\s*you\s*might\s*also\s*like'
    ]]

# Remove unwanted patterns from Genius API
def clean_lyrics(lyrics:str, artist:str) -> str:
    # Convert lyrics to lowercase for consistent matching
    lyrics = lyrics.lower()
    
    # Apply static patterns
    for regex in STATIC_CLEAN_PATTERNS:
        lyrics = regex.sub('', lyrics)

    for regex in dynamic_patterns(artist):
        lyrics = regex.sub('', lyrics)

    return lyrics.strip()

# Function to check if a song is instrumental
def is_instrumental(lyrics: str) -> bool:
    return bool(INSTRUMENTAL_PATTERN.search(lyrics))

def translate(lyrics: str, artist: str) -> str:
    # 1: Clean lyrics
    cleaned_lyrics = clean_lyrics(lyrics, artist)
    lines = re.split(r'\r\n|\r|\n', cleaned_lyrics)

    # edge case for urdu/arabic
    if detect_script(cleaned_lyrics) == "ar":
        new_lines = []
        for line in lines:
            new_lines.extend(re.split(r'(?<=[.!؟۔])\s*', line))  # Split at Urdu/Arabic sentence-ending marks
        lines = [line.strip() for line in new_lines if line.strip()]

    translated_lines = []
    for line in lines:
        # skip empty
        if not line.strip():
            translated_lines.append(line)
            continue
        
        # 2: Translate each line if it's not predominantly Hindi
        script = detect_script(line)
        translated_line = line
        if script != "hi":
            try:
                # Translate line with detected source language
                response = client.translate_text(
                    contents=[line],
                    target_language_code="hi",
                    parent=PARENT,
                    mime_type="text/plain"
                )
                translated_line = response.translations[0].translated_text
            except Exception as e:
                print(f"Translation error for script {script}: {e}")

        
        # 3: Transliterate any romanized text in the line (ex: namaste -> नमस्ते)
        words = translated_line.split()
        translated_words = []
        
        for word in words:
            if re.match(r'^[a-zA-Z'']+$', word):
                transliterated = transliterate(word, ITRANS, DEVANAGARI)
                translated_words.append(transliterated)
            else:
                translated_words.append(word)
        
        translated_lines.append(' '.join(translated_words))
    
    # Join lines back together
    translated_lyrics = '\n'.join(translated_lines)

    # 4: Translate any remaining non-Hindi text in the joined text
    non_hindi_texts = re.findall(r'[^\u0900-\u097F\s\.,!?]+', translated_lyrics)
    for text in set(non_hindi_texts):
        if text.strip():
            try:
                response = client.translate_text(
                    contents=[text],
                    target_language_code="hi",
                    parent=PARENT,
                    mime_type="text/plain"
                )
                translated_text = response.translations[0].translated_text
                # Replace whole word matches only
                translated_lyrics = translated_lyrics.replace(text, translated_text)
            except Exception as e:
                print(f"Error translating non-Hindi text '{text}': {e}")

    # 5: Final check to transliterate any remaining romanized text
    translated_lyrics = translated_lyrics.replace("'", "")
    translated_lyrics = re.sub( r"\b[a-zA-Z']+\b", lambda m: transliterate(m.group(), ITRANS, DEVANAGARI), translated_lyrics)
        
    return translated_lyrics

df = pd.read_csv('data/lyrics/lyrics.csv')
df.columns = ['artist', 'title','raw_lyrics']

# specific_entry = df.iloc[35]
# lyrics = specific_entry['raw_lyrics']
# artist = specific_entry['artist']
# print(f"Original {specific_entry['title']}: {lyrics}")
# print(f"Translated {specific_entry['title']}: {translate(lyrics, artist)}")

df = pd.read_csv('data/lyrics/lyrics.csv')
df.columns = ['artist', 'title','raw_lyrics']
df = df[df['artist'] != 'KK'] 
df = df[~df['raw_lyrics'].apply(is_instrumental)]
df['cleaned_lyrics'] = np.vectorize(translate)(df['raw_lyrics'], df['artist'])

df.drop('raw_lyrics', axis=1, inplace=True)
df.to_csv("data/lyrics/lyrics_cleaned.csv",index=False)
# df.to_clipboard()
print(df.head())
print("Dataset cleaned")