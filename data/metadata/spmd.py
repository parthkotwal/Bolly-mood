import pandas as pd

df = pd.read_csv("data/metadata/spotify_metadata.csv")
df = df[['spotify_id','title','artist','album','release_date','popularity']]
df.to_csv("data/metadata/spotify_metadata.csv", index=False)