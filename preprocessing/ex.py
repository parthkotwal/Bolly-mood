# # def translate(lyrics: str, artist: str):
# #     language_scripts = {
# #         "as": r"[\u0980-\u09FF]+(?: [\u0980-\u09FF]+)*",  # Assamese
# #         "bn": r"[\u0980-\u09FF]+(?: [\u0980-\u09FF]+)*",  # Bengali
# #         "gu": r"[\u0A80-\u0AFF]+(?: [\u0A80-\u0AFF]+)*",  # Gujarati
# #         "hi": r"[\u0900-\u097F]+(?: [\u0900-\u097F]+)*",  # Hindi
# #         "kn": r"[\u0C80-\u0CFF]+(?: [\u0C80-\u0CFF]+)*",  # Kannada
# #         "ks": r"[\u0600-\u06FF]+(?: [\u0600-\u06FF]+)*",  # Kashmiri (Perso-Arabic script)
# #         "ml": r"[\u0D00-\u0D7F]+(?: [\u0D00-\u0D7F]+)*",  # Malayalam
# #         "mr": r"[\u0900-\u097F]+(?: [\u0900-\u097F]+)*",  # Marathi
# #         "ne": r"[\u0900-\u097F]+(?: [\u0900-\u097F]+)*",  # Nepali
# #         "or": r"[\u0B00-\u0B7F]+(?: [\u0B00-\u0B7F]+)*",  # Oriya (Odia)
# #         "pa": r"[\u0A00-\u0A7F]+(?: [\u0A00-\u0A7F]+)*",  # Punjabi
# #         "sa": r"[\u0900-\u097F]+(?: [\u0900-\u097F]+)*",  # Sanskrit (Devanagari script)
# #         "sd": r"[\u0600-\u06FF]+(?: [\u0600-\u06FF]+)*",  # Sindhi (Arabic script)
# #         "ta": r"[\u0B80-\u0BFF]+(?: [\u0B80-\u0BFF]+)*",  # Tamil
# #         "te": r"[\u0C00-\u0C7F]+(?: [\u0C00-\u0C7F]+)*",  # Telugu
# #         "ur": r"[\u0600-\u06FF]+(?: [\u0600-\u06FF]+)*",  # Urdu (Perso-Arabic script)
# #     }


# #     # Remove all unnecessary characters and text from scraping
# #     # lyrics = clean_lyrics(lyrics, artist)

# #     # Collect words from all detected languages
# #     # words_to_translate = set()
# #     # for lang, pattern in language_scripts.items():
# #     #     words_to_translate.update(re.findall(pattern, lyrics))

# #     # # Include English and Romanized words
# #     # words_to_translate.update(re.findall(r"[a-zA-Z'’]+", lyrics))

# #     # # Convert set to list for batch API translation
# #     # words_to_translate = list(words_to_translate)

# #     # Dictionary to store translations
# #     # translations = {}

# #     # if words_to_translate:
# #     #     try:
# #     #         response = client.translate_text(
# #     #             contents=words_to_translate,
# #     #             target_language_code="hi",
# #     #             parent=PARENT,
# #     #             mime_type="text/plain"
# #     #         )
# #     #         # Map original words to their translated versions
# #     #         for original, translated in zip(words_to_translate, response.translations):
# #     #             translations[original] = translated.translated_text
# #     #     except Exception as e:
# #     #         print(f"Translation error: {e}")

# #     # # Replace words in lyrics with Hindi translations
# #     # for word, translated in translations.items():
# #     #     lyrics = re.sub(rf'\b{re.escape(word)}\b', translated, lyrics)

# #     # lyrics = lyrics.replace("'","")

# #     # # Transliterate remaining words until there are none
# #     # previous_lyrics = ""
# #     # max_iterations = 10
# #     # iteration = 0

# #     # while lyrics != previous_lyrics and iteration < max_iterations:
# #     #     previous_lyrics = lyrics
# #     #     remaining_romanized = re.findall(r"[a-zA-Z'’]+", lyrics)
# #     #     if not remaining_romanized:
# #     #         break

# #     #     for word in remaining_romanized:
# #     #         transliterated_word = transliterate(word, ITRANS, DEVANAGARI)
# #     #         lyrics = re.sub(rf'\b{re.escape(word)}\b', transliterated_word, lyrics)

# #     #     iteration += 1

# #     # return lyrics

# #     lyrics = clean_lyrics(lyrics, artist)
    
# #     # Dictionary to store translations for each script
# #     translations = {}
    
# #     # Process each script separately
# #     for lang, pattern in language_scripts.items():
# #         # Find all words in current script
# #         script_words = re.findall(pattern, lyrics)
        
# #         if script_words:
# #             try:
# #                 # Translate words from current script to Hindi
# #                 response = client.translate_text(
# #                     contents=script_words,
# #                     target_language_code="hi",
# #                     source_language_code=lang,  # Specify source language
# #                     parent=PARENT,
# #                     mime_type="text/plain"
# #                 )
                
# #                 # Store translations for current script
# #                 for original, translated in zip(script_words, response.translations):
# #                     translations[original] = translated.translated_text
# #             except Exception as e:
# #                 print(f"Translation error for {lang}: {e}")
    
# #     # Replace all script words with their Hindi translations
# #     for original, translated in translations.items():
# #         lyrics = re.sub(rf'\b{re.escape(original)}\b', translated, lyrics)

# #     # Handle any remaining romanized text
# #     lyrics = lyrics.replace("'", "")
    
# #     previous_lyrics = ""
# #     max_iterations = 10
# #     iteration = 0

# #     while lyrics != previous_lyrics and iteration < max_iterations:
# #         previous_lyrics = lyrics
# #         remaining_romanized = re.findall(r"[a-zA-Z'']+", lyrics)
        
# #         if not remaining_romanized:
# #             break

# #         for word in remaining_romanized:
# #             transliterated_word = transliterate(word, ITRANS, DEVANAGARI)
# #             lyrics = re.sub(rf'\b{re.escape(word)}\b', transliterated_word, lyrics)

# #         iteration += 1

# #     return lyrics

# # from pathlib import Path
# # from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
# # import pandas as pd
# # import numpy as np
# # import re
# # import os
# # agar = """ayе tumsе"""
# # print(transliterate(agar, ITRANS, DEVANAGARI))

# Row 23 (Dil Mein Hai Pyar Tera Hoton Pe Gitwa): Romanized words: pard si jaat
# Row 32 (Love you zindagi): Romanized words: y jan
# Row 47 (Teriyaan Tu Jaane): Romanized words: l s
# Row 48 (Sacchi Mohabbat): Romanized words: v
# Row 49 (Madhubala): Romanized words: par y s
# Row 57 (Jaan Leke Gayi): Romanized words: se orita se orita se
# Row 62 (Chamma Chamma (From ”Fraud Saiyaan”)): Romanized words: close
# Row 69 (Pachchai Nirame (Sakiye)): Romanized words: llaam akiyae naegidhiyae akiyae naegidhiyae
# Row 71 (Jai Ho): Romanized words: t d a m s
# Row 73 (Masti Ki Paathshala): Romanized words: h so
# Row 74 (Nazar Laaye): Non-Hindi script detected: ['ਮ', 'ਾ', 'ਹ', 'ੀ', 'ਮ']
# Row 82 (Aaruyire): Romanized words: nni
# Row 85 (Yenga Pona Raasa): Romanized words: k ndaadum k ndaadum entha
# Row 89 (Nenjae Yezhu): Romanized words: ndrum ndrum ngum p nnaalum
# Row 91 (Chinnamma Chilakkamma): Unwanted text detected: \[.*?\]
# Row 97 (Varaaga nathi): Romanized words: y agamadi n nnak p
# Row 103 (Satranga): Non-Hindi script detected: ['ਰ', 'ੁ', 'ੱ', 'ਕ', 'ਣ']
# Row 116 (Tera Yaar Hoon Main): Non-Hindi script detected: ['ਸ', 'ੱ', 'ਜ', 'ਣ', 'ਾ']
# Row 134 (Mast Magan): Non-Hindi script detected: ['ਵ', 'ੱ', 'ਖ', 'ਰ', 'ਾ']
# Row 141 (Deva Deva (Film Version)): Romanized words: m in m in
# Row 147 (You): Romanized words: clich w m ant
# Row 155 (Marne Se Pehle): Romanized words: kisis marn
# Row 159 (Mere Khayaalon Mein): Romanized words: kais churay
# Row 162 (Kasam Se): Romanized words: y h m in
# Row 163 (Humnawa): Romanized words: muh kais
# Row 164 (Sun Maahi): Romanized words: k r
# Row 173 (VEHAM): Romanized words: mp d cember vid o
# Row 174 (Nakhrey Nakhrey): Romanized words: k humar
# Row 175 (Wajah tum ho): Romanized words: saans in s
# Row 206 (China Town): Romanized words: b gaana aak
# Row 210 (Palat Meri Jaan): Non-Hindi script detected: ['ਮ', 'ਾ', 'ਇ', 'ਆ', 'ਂ']
# Row 212 (Hamein Diya Hai Aapne Dhoka): Romanized words: hum m in
# Row 216 (Mujhe Maar Daalo (Romanized)): Romanized words: jeen kah ga
# Row 218 (Yeh Raat Hai Mehtabi): Romanized words: baat s
# Row 239 (Tumhari Chup): Romanized words: s s
# Row 263 (MERCY): Non-Hindi script detected: ['ਇ', 'ਕ', 'ਵ', 'ਾ', 'ਰ']
# Row 267 (Driving Slow): Romanized words: speed chill
# Row 268 (Players): Romanized words: b at m in
# Row 271 (Abhi Toh Party Shuru Hui Hai): Romanized words: p naach
# Row 294 (Genda Phool): Non-Hindi script detected: ['ব', 'ড়', 'ল', 'ো', 'ক']
# Row 298 (Heartless (feat. Aastha Gill)): Non-Hindi script detected: ['ਮ', 'ੈ', 'ਨ', 'ੂ', 'ੰ']
# Row 302 (Paani Paani): Romanized words: ter m re
# Row 304 (Mujhe Peene Do): Romanized words: peen peen
# Row 306 (Mahiye Jinna Sohna): Romanized words: j mahiy
# Row 309 (Lo Aayi Barsaat): Romanized words: mer ayeng
# Row 317 (Rabba Mehar kari): Romanized words: m ra m ra
# Row 324 (Maa): Romanized words: seen d ke
# Row 330 (Tum Mere): Romanized words: l ter
# Row 331 (Mountain Dew): Romanized words: m iube ti nseamn tii
# Row 333 (Nayan): Romanized words: kais
# Row 337 (Vaaste): Non-Hindi script detected: ['ਮ', 'ਾ', 'ਹ', 'ੀ', 'ਆ']
# Row 338 (Thank You God): Non-Hindi script detected: ['ਕ', 'ਹ', 'ਿ', 'ੰ', 'ਦ']
# Row 358 (Bin Bulaye): Romanized words: ind pendent int rdependent
# Row 359 (Pyaar Pyaar): Romanized words: mer d
# Row 363 (Jealous): Romanized words: k
# Row 365 (Faltu Rapper): Romanized words: s bhenchod
# Row 366 (Chosen): Romanized words: indep ndent mer
# Row 369 (Plastic): Romanized words: toon k
# Row 370 (Sunn): Romanized words: jabs bhast
# Row 374 (Keede): Romanized words: gan en rgy
# Row 383 (Khaas): Romanized words: g k n g
# Row 390 (Kohinoor): Romanized words: boy
# Row 391 (One Side): Romanized words: side
# Row 395 (Wallah): Romanized words: gang
# Row 396 (Mirchi): Romanized words: sh mak
# Row 399 (Remand): Romanized words: s rd
# Row 400 (Too Hype): Romanized words: pac
# Row 401 (3:59 AM): Romanized words: x oubli s effac s
# Row 407 (Gunehgar): Romanized words: gunehgar
# Row 408 (Disco Rap): Romanized words: isliy ch ss raant
# Row 415 (Hitman): Romanized words: k waal
# Row 417 (Flex Kar): Romanized words: mer m ri
# Row 419 (Walking Miracle): Romanized words: beli ve v
# Row 422 (Drill Karte): Romanized words: th y mattr ss
# Row 428 (Company): Romanized words: saar chaiy
# Row 429 (Freeverse FEAST (Explicit)): Romanized words: peace
# Row 432 (Mera Bhai Mera Bhai): Romanized words: o
# Row 436 (#Sadak): Romanized words: hahaha
# Row 439 (MACHAYENGE 4): Romanized words: chust id g
# Row 442 (GUESS): Romanized words: main machan
# Row 443 (KR L$DA SIGN): Romanized words: cr
# Row 448 (Round One): Romanized words: mm
# Row 449 (HEAL): Romanized words: h al mujh
# Row 451 (Freeverse Feast 2): Romanized words: s s
# Row 457 (HARD): Romanized words: bitch
# Row 458 (Scene Change): Romanized words: b ta a
# Row 459 (Chalte Firte): Romanized words: pac
# Row 460 (BAJO): Romanized words: k ya t m
# Row 461 (My Time): Romanized words: m mak aye
# Row 464 (Drill): Romanized words: jais jaan ga
# Row 470 (Senorita): Romanized words: qui n t d nde
# Row 480 (Moon Rise): Romanized words: jana
# Row 484 (Main Deewana Tera): Non-Hindi script detected: ['ਤ', 'ੇ', 'ਰ', 'ੀ', 'ਆ']
# Row 485 (Fashion): Romanized words: d d
# Row 486 (Main Deewana Tera (From ”Arjun Patiala”)): Non-Hindi script detected: ['ਤ', 'ੇ', 'ਰ', 'ੀ', 'ਆ']
# Row 487 (Nain Bengali): Romanized words: jinn jehiy n
# Row 511 (Terre Pyaar Mein): Romanized words: v y
# Row 525 (Teri Jhalak Asharfi Srivalli Naina Madak Barfi): Romanized words: jay jhmuk
# Row 529 (Chal Ve Watna): Non-Hindi script detected: ['ਚ', 'ੱ', 'ਲ', 'ਵ', 'ੇ']
# Row 532 (Naina Lade  Lyrics - Dabangg3 | Javed Ali): Romanized words: dabangg gaye
# Row 565 (Pyar Hamen Kis Mod Pe): Romanized words: hum in kar
# Row 575 (Tera mera pyar): Non-Hindi script detected: ['ਸ', 'ੋ', 'ਹ', 'ਣ', 'ੀ']
# Row 631 (Bharat Ka Rahnewala Hoon): Romanized words: jis jeet
# Row 656 (Ishqam): Non-Hindi script detected: ['ਬ', 'ਿ', 'ੱ', 'ਲ', 'ੋ']
# Row 663 (Paisa): Romanized words: kamay ga tujhs
# Row 702 (Yun Hi): Romanized words: lag tujh
# Row 711 (Aga Bai (from ”Aiyyaa”)): Romanized words: hon y vid o
# Row 718 (Do Gallan Kariye Pyar Diyan): Romanized words: t hov
# Row 722 (KHYAAL RAKHYA KAR): Romanized words: chot m ra
# Row 753 (Atif Aslam - Pehli Nazar Mein (Romanized)): Romanized words: tujhs m ri
# Row 754 (Lutt Putt Gaya): Non-Hindi script detected: ['ਲ', 'ੁ', 'ੱ', 'ਟ', 'ਿ']
# Row 759 (Tum Mile): Romanized words: m in bahaar n
# Row 779 (Awein Hai): Romanized words: mil bees dus pac
# Row 781 (F16): Romanized words: f f F f
# Row 784 (Never Back Down): Romanized words: tujhm rakht
# Row 787 (Black Sheep): Romanized words: snak h art
# Row 789 (36): Romanized words: k
# Row 799 (NO CHINA): Romanized words: girlfri nd m an
# Row 799 (NO CHINA): Non-Hindi script detected: ['ਛ', 'ਡ', 'ਦ', 'ੀ']
# Row 800 (JASHAN-E-HIP-HOP): Romanized words: l gendary test d
# Row 800 (JASHAN-E-HIP-HOP): Non-Hindi script detected: ['ਗ', 'ੱ', 'ਲ', 'ਕ', 'ੁ']
# Row 809 (Speed Se Badho): Romanized words: badh s
# Row 810 (ICE): Romanized words: r gam m
# Row 810 (ICE): Non-Hindi script detected: ['ਕ', 'ੱ', 'ਖ', 'ਕ', 'ੱ']
# Row 812 (Dhaakad): Unwanted text detected: \[.*?\]
# Row 829 (Kandhe ka woh til lyrics hindi): Romanized words: lyrics
# Row 835 (Amarnath Ishwaram): Romanized words: pehl beht
# Row 864 (Kandhon Se Milte Hain Kandhe): Romanized words: milt chalt
# Row 869 (Hindustani (From ”Street Dancer 3D”)): Romanized words: d
# Row 872 (Dippu Dippu): Romanized words: r kkai th di
# Row 888 (Praan Dite Chai, Mon Dite Chai): Romanized words: aashl jur
# Row 898 (Bhari Bhari Song): Romanized words: mp mp mp
# Row 903 (Jhalla Wallah): Romanized words: matin e
# Row 909 (Esheche Raat): Romanized words: ha h kar ha at
# Row 923 (Phir Milenge Chalte Chalte): Non-Hindi script detected: ['ব', 'া', 'ব', 'ু', 'ম']
# Row 950 (Shirt Da Button (From ”Kyaa Super Kool Hain Hum”)): Non-Hindi script detected: ['ਤ', 'ੇ', 'ਰ', 'ੀ', 'ਦ']
# Row 966 (Million Dollar Dream): Romanized words: dream
# Row 979 (Million Dollar Dream (Demo)): Romanized words: th d
# Row 989 (Halkat Jawani): Non-Hindi script detected: ['ਐ', 'ਵ', 'ੇ', 'ਂ', 'ਐ']
# Row 994 (Sajna Ve Sajna): Non-Hindi script detected: ['ਸ', 'ੱ', 'ਜ', 'ਣ', 'ਾ']
# Row 999 (Shut Up & Bounce): Romanized words: y ah t ri
# Row 1001 (Dhoom Machale (Romanized)): Romanized words: danc b khabar
# Row 1013 (Shake It Saiyyan): Romanized words: g
# Row 1020 (Baal Khade): Romanized words: b ll m in
# Row 1030 (Thodi Jagah Female Version): Romanized words: ter
# Row 1041 (Chatta Rumal Kya Malum): Romanized words: x x x x x
# Row 1044 (Udja Kale Kawan): Romanized words: k jaay
# Row 1048 (Pehla Nasha Pehla Khumaar): Romanized words: sapn r h
# Row 1052 (Laaj Ko Lali): Romanized words: aauda laidauna aba ajhai chaideuna
# Row 1076 (Madari): Non-Hindi script detected: ['ਹ', 'ਾ', 'ਜ਼', 'ੀ', 'ਲ']
# Row 1084 (Jai Jai Shivshankar): Non-Hindi script detected: ['ਹ', 'ੋ', 'ਸ', 'ਾ', 'ਰ']

import pandas as pd
import re

# Define allowed Unicode ranges for scripts + English letters
allowed_ranges = [
    (0x0900, 0x097F),  # Devanagari (Hindi)
    (0x0A00, 0x0A7F),  # Gurmukhi (Punjabi)
    (0x0980, 0x09FF),  # Bengali
    (0x0A80, 0x0AFF),  # Gujarati
    (0x0B80, 0x0BFF),  # Tamil
    (0x0C00, 0x0C7F),  # Telugu
    (0x0C80, 0x0CFF),  # Kannada
    (0x0D00, 0x0D7F),  # Malayalam
    (0x0B00, 0x0B7F),  # Oriya
    (0x0041, 0x005A),  # English uppercase A-Z
    (0x0061, 0x007A),  # English lowercase a-z
    (0x0030, 0x0039),  # Digits 0-9
    (0x0020, 0x002F),  # Basic punctuation
    (0x003A, 0x0040),
    (0x005B, 0x0060),
    (0x007B, 0x007E)
]

# Create regex pattern from Unicode ranges
allowed_pattern = "[" + "".join(f"\\U{start:08X}-\\U{end:08X}" for start, end in allowed_ranges) + "]"

# Invert the pattern to find unwanted characters
unwanted_pattern = f"[^{allowed_pattern}]"


df = pd.read_csv('data/lyrics/lyrics_cleaned.csv')

# Function to find unwanted characters in a string
def find_unwanted_chars(text):
    return "".join(re.findall(unwanted_pattern, text))

# Apply function to find unwanted characters in each row
df["unwanted_chars"] = df["cleaned_lyrics"].apply(find_unwanted_chars)

# Filter rows with unwanted characters
df_with_unwanted = df[df["unwanted_chars"] != ""]

# Display results
print(df_with_unwanted)