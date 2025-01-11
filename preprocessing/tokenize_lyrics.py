from transformers import AutoTokenizer, AutoModelForMaskedLM
import pandas as pd

tokenizer = AutoTokenizer.from_pretrained("google/muril-base-cased")
model = AutoModelForMaskedLM.from_pretrained("google/muril-base-cased")