import pandas as pd
import plotly.express as px
from collections import defaultdict
import pycountry

# Load data
df = pd.read_csv("web_engineering_combined.csv")

# Ensure citations are numeric
df['citations'] = pd.to_numeric(df['citations'], errors='coerce')
df = df.dropna(subset=['citations'])

# --- Utility to split text fields ---
def parse_list(text):
    if pd.isna(text):
        return []
    return [item.strip() for item in text.replace(';', ',').split(',') if item.strip()]

# Authors
df['author_list'] = df['authors'].apply(parse_list)

# Affiliations
df['affiliation_list'] = df['affiliations'].apply(parse_list)

# --- Citations per Author ---
citations_per_author = defaultdict(float)
for _, row in df.iterrows():
    authors = row['author_list']
    if authors:
        share = row['citations'] / len(authors)
        for author in authors:
            citations_per_author[author] += share

df_authors = pd.DataFrame(list(citations_per_author.items()), columns=["author", "total_citations"])
df_authors["total_citations"] = df_authors["total_citations"].round(1)
df_authors = df_authors.sort_values(by="total_citations", ascending=False).head(10)
df_authors['truncated'] = df_authors['author'].apply(lambda x: x if len(x) <= 30 else x[:30] + '...')

fig_authors = px.bar(
    df_authors,
    x="total_citations",
    y="truncated",
    orientation='h',
    title="Top 10 Authors by Total Citations",
    labels={"total_citations": "Total Citations", "truncated": "Author"},
    hover_data={"author": True, "truncated": False}
)
fig_authors.update_layout(yaxis={'categoryorder': 'total ascending'})
fig_authors.show()

# --- Citations per Affiliation ---
citations_per_affil = defaultdict(float)
for _, row in df.iterrows():
    affils = row['affiliation_list']
    if affils:
        share = row['citations'] / len(affils)
        for aff in affils:
            citations_per_affil[aff] += share

df_affils = pd.DataFrame(list(citations_per_affil.items()), columns=["affiliation", "total_citations"])
df_affils["total_citations"] = df_affils["total_citations"].round(1)
df_affils = df_affils.sort_values(by="total_citations", ascending=False).head(10)
df_affils['truncated'] = df_affils['affiliation'].apply(lambda x: x if len(x) <= 30 else x[:30] + '...')

fig_affils = px.bar(
    df_affils,
    x="total_citations",
    y="truncated",
    orientation='h',
    title="Top 10 Affiliations by Total Citations",
    labels={"total_citations": "Total Citations", "truncated": "Affiliation"},
    hover_data={"affiliation": True, "truncated": False}
)
fig_affils.update_layout(yaxis={'categoryorder': 'total ascending'})
fig_affils.show()

# --- Citations per Country (from affiliation strings) ---
country_names = [country.name for country in pycountry.countries]
country_names += ['USA', 'UK']  # Add common abbreviations

def extract_countries(text):
    if pd.isna(text):
        return []
    countries_found = []
    for entry in text.replace(';', ',').split(','):
        entry = entry.strip()
        for country in country_names:
            if country in entry:
                countries_found.append(country)
                break
    return list(set(countries_found))

df['country_list'] = df['affiliations'].apply(extract_countries)

citations_per_country = defaultdict(float)
for _, row in df.iterrows():
    countries = row['country_list']
    if countries:
        share = row['citations'] / len(countries)
        for country in countries:
            citations_per_country[country] += share

df_countries = pd.DataFrame(list(citations_per_country.items()), columns=["country", "total_citations"])
df_countries["total_citations"] = df_countries["total_citations"].round(1)
df_countries = df_countries.sort_values(by="total_citations", ascending=False).head(10)
df_countries['truncated'] = df_countries['country'].apply(lambda x: x if len(x) <= 30 else x[:30] + '...')

fig_countries = px.bar(
    df_countries,
    x="total_citations",
    y="truncated",
    orientation='h',
    title="Top 10 Countries by Total Citations",
    labels={"total_citations": "Total Citations", "truncated": "Country"},
    hover_data={"country": True, "truncated": False}
)
fig_countries.update_layout(yaxis={'categoryorder': 'total ascending'})
fig_countries.show()
