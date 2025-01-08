import os
import pandas as pd
import re
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI, GURMUKHI

df = pd.read_csv('data/lyrics.csv')

def detect_script(lyrics:str):
    devanagari_pattern = r'[\u0900-\u097F]'  # Unicode range for Devanagari script
    devanagari_count = len(re.findall(devanagari_pattern, lyrics))
    
    if devanagari_count > 0:
        return 'devanagari'
    else:
        return 'roman'

def process_devanagari(lyrics:str) -> str:
    return transliterate(lyrics, DEVANAGARI, ITRANS)

def process_romanized(lyrics: str):
    lyrics = re.sub(r'\s+', ' ', lyrics).strip()
    lyrics = re.sub(r'[^\w\s\u0900-\u097F]', '', lyrics)
    lyrics = lyrics.lower()
    return lyrics


def clean_lyrics(lyrics:str):
    unwanted_patterns = [
    r'\b(embed|you might also like|related songs|other songs you might like|advertisement|promo)\b',  # Exact match for common terms
    r'\[.*?\]',  # Any text within square brackets
    r'http[s]?://\S+',  # URLs 
    r'--+',  # Long dashes or similar
    r'^\s*$',  # Empty lines or lines containing only spaces
    r"^\d+\s*Contributor.*?Lyrics" # n ContributorsSongName Lyrics
    ]

    for pattern in unwanted_patterns:
        lyrics = re.sub(pattern, '', lyrics, flags=re.IGNORECASE)
    lyrics = re.sub(r'\[.*?\]', '', lyrics)
    lyrics = re.sub(r'\s+', ' ', lyrics).strip()
    lyrics = re.sub(r'[^\w\s\u0900-\u097F]', '', lyrics)
    lyrics = lyrics.lower()
    return lyrics

def clean_and_standardize(lyrics:str):
    lyrics = clean_lyrics(lyrics)
    script = detect_script(lyrics)
    if script == 'devanagari':
        lyrics = process_devanagari(lyrics)
    else:
        lyrics = process_romanized(lyrics)
    return lyrics.lower()


# def standardize(lyrics:str, target_script="devanagari"):
#     # translator = Translator()
#     lines = lyrics.split('\n')
#     processed = []
#     for line in lines:

#         processed_line = transliterate(line, DEVANAGARI, ITRANS)

#         processed.append(processed_line)

#     return '\n'.join(processed)

print(df['lyrics'][4])
print(f"Cleaned: {clean_and_standardize(df['lyrics'][4])}")