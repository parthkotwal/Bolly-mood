import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI, GURMUKHI

df = pd.read_csv('data/lyrics.csv')

def detect_script(lyrics:str):
    devanagari_pattern = r'[\u0900-\u097F]'  # Unicode range for Devanagari script
    devanagari_count = len(re.findall(devanagari_pattern, lyrics))

    gurmukhi_pattern = r'[\u0A00-\u0A7F]'
    gurmukhi_count = len(re.findall(gurmukhi_pattern, lyrics))
    
    if devanagari_count > 0:
        return 'devanagari'
    elif gurmukhi_count > 0:
        return 'gurmukhi'
    else:
        return 'roman'

def process_devanagari(lyrics:str) -> str:
    return transliterate(lyrics, DEVANAGARI, ITRANS)

def process_gurmukhi(lyrics:str) -> str:
    return transliterate(lyrics, GURMUKHI, ITRANS)

def process_romanized(lyrics: str):
    lyrics = re.sub(r'\s+', ' ', lyrics).strip()
    lyrics = re.sub(r'[^\w\s\u0900-\u097F]', '', lyrics)
    lyrics = lyrics.lower()
    return lyrics


def clean_lyrics(lyrics:str):
    unwanted_patterns = [
    r'\b(embed|you might also like|related songs|other songs you might like|advertisement|promo|Embed|1Embed)\b',  # Exact match for common terms
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

# print(df['lyrics'][4])
# print(f"Cleaned: {clean_and_standardize(df['lyrics'][4])}")



df.columns = ['artist', 'title','raw_lyrics']
df['cleaned_lyrics'] = np.vectorize(clean_and_standardize)(df['raw_lyrics'])
# print(df['cleaned_lyrics'])

def remove_non_ascii(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)
vectorized_remove_non_ascii = np.vectorize(remove_non_ascii)(df['cleaned_lyrics'])

df = df[df['cleaned_lyrics'].str.len() >= 10]
df['cleaned_lyrics'] = df['cleaned_lyrics'].str.replace('ऑ', 'au')

stop_words = set(stopwords.words('hinglish'))
df['cleaned_lyrics'] = df['cleaned_lyrics'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))

df.to_csv("data/lyrics_cleaned.csv",index=False)