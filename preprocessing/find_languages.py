import pandas as pd

# Sample data (replace with your actual dataset)
df = pd.read_csv('data/lyrics_cleaned.csv')

# Set for storing unique non-English characters
unique_non_english = set()

# Define the Unicode range for English (basic Latin)
english_unicode_range = (0x0000, 0x007F)  # Basic Latin range

def is_english_char(char):
    """Check if a character is within the English Unicode range"""
    return english_unicode_range[0] <= ord(char) <= english_unicode_range[1]

def detect_non_english_characters(text):
    """Detect non-English characters in a string and store unique ones"""
    for char in text:
        if not is_english_char(char):
            unique_non_english.add(char)

# Iterate through your dataset
for index, row in df.iterrows():
    detect_non_english_characters(row['cleaned_lyrics'])  # Replace 'raw_lyrics' with the appropriate column name

# Print one unique non-English character from each language
for char in unique_non_english:
    print(f"Character: {char}, Unicode: {hex(ord(char))}")
