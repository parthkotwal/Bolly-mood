import rapidfuzz.fuzz as fuzz

genius_title = 'कहिले तिम्रो पछ्यौरीमा अल्झेँ'
spotify_title = 'Kahile Timro Pachhurima'
print(fuzz.ratio(genius_title, spotify_title))