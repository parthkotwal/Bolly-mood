import os
import pandas as pd
df = pd.read_csv('data/lyrics.csv')

import re
def remove_prefix(lyrics):
    lyrics = re.sub(r"^\d+\s*Contributor.*?Lyrics", "", lyrics) 
    lyrics = lyrics.strip()
    return lyrics


from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI
def standardize_text(lyrics:str):
    return transliterate(lyrics, ITRANS, DEVANAGARI)

s = df.iloc[0,2]
print(standardize_text(s))