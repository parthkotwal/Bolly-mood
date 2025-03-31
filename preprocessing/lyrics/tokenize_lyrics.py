from transformers import AutoTokenizer, AutoModelForMaskedLM
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset

tokenizer = AutoTokenizer.from_pretrained("google/muril-base-cased")
model = AutoModelForMaskedLM.from_pretrained("google/muril-base-cased")
df = pd.read_csv("data/lyrics/lyrics_cleaned_labelled.csv")

def tokenize_lyrics(lyrics:str):
    return tokenizer(lyrics, padding='max_length', truncation=True, max_length=128)
df['tokenized_lyrics'] = [tokenize_lyrics(lyric) for lyric in df['cleaned_lyrics']]

def encode_lyrics(tokenized_lyrics):
    return {'input_ids': tokenized_lyrics['input_ids'], 'attention_mask': tokenized_lyrics['attention_mask']}
df['encoded_lyrics'] = [encode_lyrics(lyric) for lyric in df['tokenized_lyrics']]

labelencoder = LabelEncoder()
df['mood'] = labelencoder.fit_transform(df['mood'])

train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['mood'], random_state=42)
train_df, val_df = train_test_split(train_df, test_size=0.1, stratify=train_df['mood'], random_state=42)


class LyricsDataset(Dataset):
    def __init__(self, df):
        self.input_ids = [x['input_ids'] for x in df['tokenized_lyrics']]
        self.attention_mask = [x['attention_mask'] for x in df['tokenized_lyrics']]
        self.labels = df['mood'].tolist()

    def __getitem__(self, idx):
        return {
            'input_ids': torch.tensor(self.input_ids[idx], dtype=torch.long),
            'attention_mask': torch.tensor(self.attention_mask[idx], dtype=torch.long),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }
    
    def __len__(self):
        return len(self.input_ids)

torch.save(LyricsDataset(train_df), './data/lyrics/lyrics_train.pt')
torch.save(LyricsDataset(val_df), './data/lyrics/lyrics_val.pt')
torch.save(LyricsDataset(test_df), './data/lyrics/lyrics_test.pt')