import re
import pandas as pd

def validate_preprocessing(df):
    issues = []

    for idx, row in df.iterrows():
        lyrics = row["cleaned_lyrics"]
        title = row["title"]
        
        # 1 Check for unwanted text patterns
        unwanted_patterns = [
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
            r'x2',
            r'x3',
            r'x4',
            r'x5',
            r'x6',
            r'x7',
            r'x8'
        ]
    
        for pattern in unwanted_patterns:
            if re.search(pattern, lyrics, re.IGNORECASE):
                issues.append((idx, title, f"Unwanted text detected: {pattern}"))

        # 2️ Check for remaining Romanized Hindi (Latin script)
        romanized_words = re.findall(r'[a-zA-Z]+', lyrics)
        if romanized_words:
            issues.append((idx, title, f"Romanized words: {' '.join(romanized_words[:5])}"))  # Show first 5 words for reference

        # 3️ Check for non-Hindi scripts
        non_hindi_chars = re.findall(r'[\u0980-\u0D7F]', lyrics)  # Bengali, Tamil, Telugu, etc.
        if non_hindi_chars:
            issues.append((idx, title, f"Non-Hindi script detected: {non_hindi_chars[:5]}"))

        # 4️ Check for empty or corrupted lyrics 
        if not lyrics.strip():
            issues.append((idx, title, "Empty lyrics"))

    return issues

df = pd.read_csv('data/lyrics/lyrics_cleaned.csv')
issues = validate_preprocessing(df)

# Display detected issues
if issues:
    for issue in issues:  # Show first 10 issues
        print(f"Row {issue[0]} ({issue[1]}): {issue[2]}")
    print(f"\nTotal issues found: {len(issues)}")
else:
    print("All lyrics are completely preprocessed!")

df.to_clipboard()