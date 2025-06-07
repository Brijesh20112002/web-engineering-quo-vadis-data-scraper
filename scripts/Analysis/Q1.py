import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
import re
import nltk
from keybert import KeyBERT

# Download NLTK tokenizer data
nltk.download('punkt')

# Initialize KeyBERT model
kw_model = KeyBERT()

# === Load CSV ===
file_path = 'web_engineering_combined.csv'  # Your CSV file
df = pd.read_csv(file_path)

# === Step 1: Clean original keywords (NO stemming) ===
def clean_keywords(text):
    if pd.isna(text):
        return []
    text = text.lower()
    keywords = re.split(r';|,|\n', text)
    return [kw.strip() for kw in keywords if kw.strip()]

# === Step 2: Extract keywords from abstract using KeyBERT (NO stemming) ===
def extract_keybert_keywords(text, top_n=10):
    if pd.isna(text) or len(text.strip()) == 0:
        return []
    try:
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)
        return [kw[0].lower() for kw in keywords]
    except Exception as e:
        print(f"KeyBERT extraction error: {e}")
        return []

# === Step 3: Create final_keywords column ===
final_keywords = []
for idx, row in df.iterrows():
    year = int(row['year'])
    if year < 2024:
        kws = clean_keywords(row['keywords'])
    else:
        kws = extract_keybert_keywords(row['abstract'])
    final_keywords.append(kws)

df['final_keywords'] = final_keywords

# === Step 4: Build topic-year count matrix ===
year_topic_counts = defaultdict(lambda: defaultdict(int))

for _, row in df.iterrows():
    year = int(row['year'])
    for kw in row['final_keywords']:
        year_topic_counts[kw][year] += 1

topic_year_df = pd.DataFrame(year_topic_counts).T.fillna(0)

# === Step 5: Limit to top 15 topics by total frequency ===
top_topics = topic_year_df.sum(axis=1).sort_values(ascending=False).head(15).index
topic_year_df = topic_year_df.loc[top_topics]

# === Step 6: Sort columns (years) ===
topic_year_df = topic_year_df[[2019, 2020, 2021, 2022, 2023, 2024]]

# === Step 7: Plot heatmap ===
plt.figure(figsize=(14, 9))
sns.heatmap(topic_year_df, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, linecolor='gray')
plt.title("Top 15 Research Topics by Year (2019–2024)", fontsize=16)
plt.xlabel("Year")
plt.ylabel("Research Topics (Full Name)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
