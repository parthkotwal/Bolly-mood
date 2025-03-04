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
df = df[df['artist'] != 'KK']

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

# Dynamic patterns function
def get_dynamic_patterns(artist: str):
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

    # Apply dynamic patterns
    dynamic_patterns = get_dynamic_patterns(artist)
    for regex in dynamic_patterns:
        lyrics = regex.sub('', lyrics)

    return re.sub(r'\s+', ' ', lyrics).strip()

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
        "en": (0x0020, 0x007E)   # English
    }
    
    char_counts = {script: 0 for script in script_ranges}
    for char in lyrics:
        code = ord(char)
        for script, (start, end) in script_ranges.items():
            if start <= code <= end:
                char_counts[script] += 1
                break
    
    # Return the script with the most characters, or None if no matches
    if any(char_counts.values()):
        return max(char_counts.items(), key=lambda x: x[1])[0]
    
    return None

# Transliterate ANY remaining romanized lyrics
def transliterate_romanized(translated_lyrics:str):
    previous_lyrics = ""
    max_iterations = 10
    iteration = 0

    while translated_lyrics != previous_lyrics and iteration < max_iterations:
        previous_lyrics = translated_lyrics
        remaining_romanized = re.findall(r"[a-zA-Z'']+", translated_lyrics)
        
        if not remaining_romanized:
            break

        for word in remaining_romanized:
            transliterated_word = transliterate(word, ITRANS, DEVANAGARI)
            translated_lyrics = re.sub(rf'\b{re.escape(word)}\b', transliterated_word, translated_lyrics)

        iteration += 1
        
    return translated_lyrics

def translate(lyrics: str, artist: str) -> str:
    # Clean lyrics first
    lyrics = clean_lyrics(lyrics, artist)
    
    # Split lyrics into lines
    lines = lyrics.split('\n')
    translated_lines = []
    
    for line in lines:
        if not line.strip():
            translated_lines.append(line)
            continue
            
        # Detect script of the line
        script = detect_script(line)

        # if script is hindi, then skip
        if script == "hi":
            translated_lines.append(line)

        # if not, then do translation
        else:
            try:
                # Translate line with detected source language
                response = client.translate_text(
                    contents=[line],
                    target_language_code="hi",
                    source_language_code=script,
                    parent=PARENT,
                    mime_type="text/plain"
                )
                translated_lines.append(response.translations[0].translated_text)
            except Exception as e:
                print(f"Translation error for script {script}: {e}")
                translated_lines.append(line)
        

        # Handle any romanized text into devanagari (ex: namaste -> नमस्ते)
        words = line.split()
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

    # Detect any remaining non-Hindi, non-Latin text for translation
    non_hindi_texts = re.findall(r'[^\u0900-\u097F\s\.,!?]+', translated_lyrics)
    if non_hindi_texts:
        for text in set(non_hindi_texts):  # Remove duplicates for efficiency
            try:
                response = client.translate_text(
                    contents=[text],
                    target_language_code="hi",
                    parent=PARENT,
                    mime_type="text/plain"
                )
                translated_text = response.translations[0].translated_text
                translated_lyrics = re.sub(rf'\b{re.escape(text)}\b', translated_text, translated_lyrics)
            except Exception as e:
                print(f"Error translating non-Hindi text '{text}': {e}")

    # Final pass for any remaining Latin script words
    translated_lyrics = translated_lyrics.replace("'", "")
    
    return transliterate_romanized(translated_lyrics)


specific_entry = df.iloc[227]
lyrics = specific_entry['raw_lyrics']
artist = specific_entry['artist']
print(f"Original {specific_entry['title']}: {specific_entry}")
print(f"Translated {specific_entry['title']}: {translate(lyrics, artist)}")

# df['cleaned_lyrics'] = np.vectorize(translate)(df['raw_lyrics'], df['artist'])

# df.drop('raw_lyrics', axis=1, inplace=True)
# df.to_csv("data/lyrics/lyrics_cleaned.csv",index=False)
# # df.to_clipboard()
# print(df.head())
# print("Dataset cleaned")