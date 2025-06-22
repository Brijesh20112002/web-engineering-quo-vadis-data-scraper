import pandas as pd
from collections import Counter
import plotly.express as px
import re
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Load CSV
df = pd.read_csv('web_engineering_combined.csv')

# -----------------------------------------
# Step 1: Clean & Parse Utility
# -----------------------------------------
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

# -----------------------------------------
# AUTHORS ANALYSIS (unchanged)
# -----------------------------------------
df['author_list'] = df['authors'].apply(smart_split)
author_counter = Counter()
for authors in df['author_list']:
    unique_authors = set(authors)  # Remove duplicates per paper
    author_counter.update(unique_authors)

author_df = pd.DataFrame(author_counter.items(), columns=['Author', 'Publications'])
top_authors = author_df.sort_values(by='Publications', ascending=False).head(10)

fig_authors = px.bar(
    top_authors[::-1],
    x='Publications',
    y='Author',
    orientation='h',
    title='🌟 Top 10 Authors by Unique Publications',
    color='Publications',
    color_continuous_scale='blues',
    text='Publications'
)
fig_authors.update_traces(textposition='outside')
fig_authors.show()

# -----------------------------------------
# AFFILIATION ANALYSIS (improved)
# -----------------------------------------
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

df['affiliation_list'] = df['affiliations'].apply(smart_split).apply(normalize_affiliations)

aff_counter = Counter()
for aff_list in df['affiliation_list']:
    aff_counter.update(aff_list)

aff_df = pd.DataFrame(aff_counter.items(), columns=['Affiliation', 'Publications'])
top_affiliations = aff_df.sort_values(by='Publications', ascending=False).head(10)

fig_aff = px.bar(
    top_affiliations[::-1],
    x='Publications',
    y='Affiliation',
    orientation='h',
    title='🏛️ Top 10 Affiliations by Unique Publications',
    color='Publications',
    color_continuous_scale='teal',
    text='Publications'
)
fig_aff.update_traces(textposition='outside')
fig_aff.show()

# -----------------------------------------
# COUNTRY ANALYSIS (unchanged)
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
top_countries = country_df.sort_values(by='Publications', ascending=False).head(10)
top_countries['Country'] = top_countries['Country'].str.title()

fig_country = px.bar(
    top_countries[::-1],
    x='Publications',
    y='Country',
    orientation='h',
    title='🌍 Top 10 Countries by Unique Paper Contributions',
    color='Publications',
    color_continuous_scale='viridis',
    text='Publications'
)
fig_country.update_traces(textposition='outside')
fig_country.show()
