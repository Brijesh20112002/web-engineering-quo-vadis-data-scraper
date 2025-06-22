from collections import Counter
import matplotlib.pyplot as plt

top_topics_set = set(top_topics)
author_counter = Counter()

for _, row in df.iterrows():
    if any(kw in top_topics_set for kw in row['final_keywords']):
        if pd.isna(row['authors']):
            continue
        authors = re.split(r';|,|\n', row['authors'])
        authors = [a.strip() for a in authors if a.strip()]
        author_counter.update(authors)

top_authors = author_counter.most_common(10)

authors, counts = zip(*top_authors)

plt.figure(figsize=(10, 6))
bars = plt.barh(authors, counts, color=sns.color_palette("flare", len(authors)))
plt.xlabel("Number of Papers")
plt.title("Top 10 Authors Publishing in Top Topics (2019–2024)")
plt.gca().invert_yaxis()

for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, f"{int(width)}", va='center')

plt.tight_layout()
plt.show()


import pandas as pd
from collections import Counter
import plotly.express as px
import re
import spacy
import plotly.io as pio

# Load NLP model
nlp = spacy.load("en_core_web_sm")

pio.renderers.default = 'notebook' 

def smart_split(text):
    if pd.isna(text):
        return []
    # split on ; | & and also comma before country (handled later)
    parts = re.split(r'[;|&]', text)
    # remove duplicates but keep order
    seen = set()
    result = []
    for p in parts:
        p = p.strip()
        if p and p not in seen:
            seen.add(p)
            result.append(p)
    return result

def normalize_affiliations(aff_list):
    normalized = []
    for aff in aff_list:
        # Fix some common typos here
        aff = aff.replace('Gemerany', 'Germany')
        aff = aff.replace('Univeristy', 'University')
        aff = aff.replace('Universtiy', 'University')
        aff = aff.replace('Univ.', 'University')
        aff = aff.replace('Univ', 'University')
        aff = aff.strip()
        normalized.append(aff)
    # Deduplicate normalized affiliations per paper
    return list(dict.fromkeys(normalized))

# Wrap long affiliation names by inserting <br> every N characters
def wrap_label(label, width=30):
    return '<br>'.join([label[i:i+width] for i in range(0, len(label), width)])
    
df['affiliation_list'] = df['affiliations'].apply(smart_split).apply(normalize_affiliations)

aff_counter = Counter()
for aff_list in df['affiliation_list']:
    aff_counter.update(aff_list)

aff_df = pd.DataFrame(aff_counter.items(), columns=['Affiliation', 'Publications'])
top_affiliations = aff_df.sort_values(by='Publications', ascending=False).head(10)
top_affiliations['Affiliation'] = top_affiliations['Affiliation'].apply(lambda x: wrap_label(x, 30))

fig_aff = px.bar(
    top_affiliations[::-1],
    x='Publications',
    y='Affiliation',
    orientation='h',
    title='🏛️ Top 10 Affiliations by Unique Publications',
    color='Publications',
    color_continuous_scale=px.colors.sequential.Magenta,
    text='Publications'
)

fig_aff.update_layout(
    xaxis_title='Number of Publications',
    yaxis_title='Affiliation',
    margin=dict(l=250, r=20, t=50, b=50),  # increase left margin
    height=900  # increase height for readability
)

fig_aff.update_xaxes(dtick=2)
fig_aff.update_traces(textposition='outside')
fig_aff.show()

import pandas as pd
from collections import Counter
import plotly.express as px
import re
import spacy
import plotly.io as pio

# Load NLP model
nlp = spacy.load("en_core_web_sm")

pio.renderers.default = 'notebook' 

def smart_split(text):
    if pd.isna(text):
        return []
    # split on ; | & and also comma before country (handled later)
    parts = re.split(r'[;|&]', text)
    # remove duplicates but keep order
    seen = set()
    result = []
    for p in parts:
        p = p.strip()
        if p and p not in seen:
            seen.add(p)
            result.append(p)
    return result

def normalize_affiliations(aff_list):
    normalized = []
    for aff in aff_list:
        # Fix some common typos here
        aff = aff.replace('Gemerany', 'Germany')
        aff = aff.replace('Univeristy', 'University')
        aff = aff.replace('Universtiy', 'University')
        aff = aff.replace('Univ.', 'University')
        aff = aff.replace('Univ', 'University')
        aff = aff.strip()
        normalized.append(aff)
    # Deduplicate normalized affiliations per paper
    return list(dict.fromkeys(normalized))

# Wrap long affiliation names by inserting <br> every N characters
def wrap_label(label, width=30):
    return '<br>'.join([label[i:i+width] for i in range(0, len(label), width)])
    
df['affiliation_list'] = df['affiliations'].apply(smart_split).apply(normalize_affiliations)

aff_counter = Counter()
for aff_list in df['affiliation_list']:
    aff_counter.update(aff_list)

aff_df = pd.DataFrame(aff_counter.items(), columns=['Affiliation', 'Publications'])
top_affiliations = aff_df.sort_values(by='Publications', ascending=False).head(10)
top_affiliations['Affiliation'] = top_affiliations['Affiliation'].apply(lambda x: wrap_label(x, 30))

fig_aff = px.bar(
    top_affiliations[::-1],
    x='Publications',
    y='Affiliation',
    orientation='h',
    title='🏛️ Top 10 Affiliations by Unique Publications',
    color='Publications',
    color_continuous_scale=px.colors.sequential.Magenta,
    text='Publications'
)

fig_aff.update_layout(
    xaxis_title='Number of Publications',
    yaxis_title='Affiliation',
    margin=dict(l=250, r=20, t=50, b=50),  # increase left margin
    height=900  # increase height for readability
)

fig_aff.update_xaxes(dtick=2)
fig_aff.update_traces(textposition='outside')
fig_aff.show()


# -----------------------------------------
# COUNTRY ANALYSIS 
# -----------------------------------------
def extract_countries(aff_list):
    countries_in_paper = set()
    for aff in aff_list:
        doc = nlp(aff)
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geo-Political Entity
                countries_in_paper.add(ent.text.strip())
    return list(countries_in_paper)

df['country_list'] = df['affiliation_list'].apply(extract_countries)

# Normalize country names (basic fixes)
country_counter = Counter()
for country_list in df['country_list']:
    unique_countries = set([c.lower().strip() for c in country_list])
    country_counter.update(unique_countries)

country_df = pd.DataFrame(country_counter.items(), columns=['Country', 'Publications'])
top_countries = country_df.sort_values(by='Publications', ascending=False).head(15)
top_countries['Country'] = top_countries['Country'].str.title()

fig_country = px.bar(
    top_countries[::-1],
    x='Publications',
    y='Country',
    orientation='h',
    title='🌍 Top 15 Countries by Unique Paper Contributions',
    color='Publications',
    color_continuous_scale=px.colors.sequential.Magenta,
    text='Publications'
)
fig_country.update_traces(textposition='outside')
fig_country.show()