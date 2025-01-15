import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI, GURMUKHI, TAMIL, BENGALI

df = pd.read_csv('data/lyrics.csv')

def detect_script(lyrics:str):
    devanagari_pattern = r'[\u0900-\u097F]'  # Unicode range for Devanagari script
    devanagari_count = len(re.findall(devanagari_pattern, lyrics))

    gurmukhi_pattern = r'[\u0A00-\u0A7F]'
    gurmukhi_count = len(re.findall(gurmukhi_pattern, lyrics))

    tamil_pattern = r'[\u0B80-\u0BFF]'
    tamil_count = len(re.findall(tamil_pattern, lyrics))

    bengali_pattern = r'[\u0980-\u09FF]'
    bengali_count = len(re.findall(bengali_pattern, lyrics))
    
    if devanagari_count > 0:
        return 'devanagari'
    elif gurmukhi_count > 0:
        return 'gurmukhi'
    elif tamil_count > 0:
        return 'tamil'
    elif bengali_count > 0:
        return 'bengali'
    else:
        return 'roman'

def process_devanagari(lyrics:str) -> str:
    return transliterate(lyrics, DEVANAGARI, ITRANS)

def process_gurmukhi(lyrics:str) -> str:
    return transliterate(lyrics, GURMUKHI, ITRANS)

def process_tamil(lyrics:str) -> str:
    return transliterate(lyrics, TAMIL, ITRANS)

def process_bengali(lyrics:str) -> str:
    return transliterate(lyrics, BENGALI, ITRANS)

def process_romanized(lyrics: str):
    lyrics = re.sub(r'\s+', ' ', lyrics).strip()
    lyrics = re.sub(r'[^\w\s\u0900-\u097F]', '', lyrics)
    lyrics = lyrics.lower()
    return lyrics


def clean_lyrics(lyrics:str):
    unwanted_patterns = [
    r'\b(embed|you might also like|related songs|other songs you might like|advertisement|promo|Embed|1Embed|2Embed)\b',  # Exact match for common terms
    r'\[.*?\]',  # Any text within square brackets
    r'http[s]?://\S+',  # URLs 
    r'--+',  # Long dashes or similar
    r'^\s*$',  # Empty lines or lines containing only spaces
    r"^\d+\s*Contributor.*?Lyrics", # n ContributorsSongName Lyrics
    r'embed',
    ]

    for pattern in unwanted_patterns:
        lyrics = re.sub(pattern, '', lyrics, flags=re.IGNORECASE)
    lyrics = re.sub(r'\[.*?\]', '', lyrics)
    lyrics = re.sub(r'\s+', ' ', lyrics).strip()
    lyrics = re.sub(r'[^\w\s\u0A00-\u0A7F]', '', lyrics)
    lyrics = re.sub(r'[^\w\s\u0900-\u097F]', '', lyrics)
    lyrics = lyrics.lower()
    return lyrics

def clean_and_standardize(lyrics:str):
    lyrics = clean_lyrics(lyrics)
    script = detect_script(lyrics)
    if script == 'devanagari':
        lyrics = process_devanagari(lyrics)
    elif script == 'gurmukhi':
        lyrics = process_gurmukhi(lyrics)
    elif script == 'tamil':
        lyrics = process_tamil(lyrics)
    elif script == 'bengali':
        lyrics = process_bengali(lyrics)
    else:
        lyrics = process_romanized(lyrics)
    return lyrics.lower()


df.columns = ['artist', 'title','raw_lyrics']
df = df[df['artist'] != 'KK']
df = df[df['title'] != 'Memu Aagamu']
df['cleaned_lyrics'] = np.vectorize(clean_and_standardize)(df['raw_lyrics'])

df = df[df['cleaned_lyrics'].str.len() >= 10]
df['cleaned_lyrics'] = df['cleaned_lyrics'].str.replace('ऑ', 'au')
df['cleaned_lyrics'] = df['cleaned_lyrics'].str.replace('ढ़', 'dh')
df['cleaned_lyrics'] = df['cleaned_lyrics'].str.replace('ன', 'n')

stop_words = set(stopwords.words('hinglish'))
df['cleaned_lyrics'] = df['cleaned_lyrics'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))
df = df[df['cleaned_lyrics'] != "song instrumental"]
df.drop('raw_lyrics',inplace=True,axis=1)

df.to_csv("data/lyrics_cleaned.csv",index=False)