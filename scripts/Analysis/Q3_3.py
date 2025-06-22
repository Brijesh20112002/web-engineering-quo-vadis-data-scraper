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
    hover_data={"author": True, "truncated": False},
    color='total_citations',
    color_continuous_scale=px.colors.sequential.Magenta
)
fig_authors.update_layout(yaxis={'categoryorder': 'total ascending'})
fig_authors.show()


import pycountry
from collections import defaultdict
import pandas as pd
import plotly.express as px

# Build country names set for filtering
country_names = {country.name.lower() for country in pycountry.countries}
country_names.update({'usa', 'uk', 'united states', 'united kingdom'})

# --- Citations and paper titles per affiliation ---
citations_per_affil = defaultdict(float)
papers_per_affil = defaultdict(set)  # store paper titles (or IDs)

for _, row in df.iterrows():
    affils = row['affiliation_list']
    
    if not isinstance(affils, list) or not affils:
        continue
    
    share = row['citations'] / len(affils) if row['citations'] > 0 else 0
    
    for aff in affils:
        clean_aff = aff.lower()
        if clean_aff in country_names:
            continue
        citations_per_affil[aff] += share
        papers_per_affil[aff].add(row['title'])  # or row['paper_id'] if you prefer

# Create DataFrame
data = []
for aff, citations in citations_per_affil.items():
    papers = papers_per_affil[aff]
    paper_list = '; '.join(list(papers)[:5])  # limit to first 5 to avoid overly long hover text
    data.append({
        "Affiliation": aff,
        "Total Citations": round(citations, 1),
        "Papers": paper_list + ('...' if len(papers) > 5 else '')
    })

df_affils = pd.DataFrame(data)
df_affils = df_affils.sort_values(by="Total Citations", ascending=False).head(10)
df_affils['Wrapped Affiliation'] = df_affils['Affiliation'].apply(lambda x: wrap_label(x, 30))

# Plot
fig_affils = px.bar(
    df_affils[::-1],
    x="Total Citations",
    y="Wrapped Affiliation",
    orientation='h',
    title="🏛️ Top 10 Affiliations by Total Citations",
    labels={"Total Citations": "Total Citations", "Wrapped Affiliation": "Affiliation"},
    color='Total Citations',
    color_continuous_scale=px.colors.sequential.Magenta,
    text="Total Citations",
    hover_data={"Papers": True, "Total Citations": True, "Wrapped Affiliation": False}
)

fig_affils.update_layout(
    xaxis_title="Total Citations",
    yaxis_title="Affiliation",
    margin=dict(l=250, r=20, t=50, b=50),
    height=900
)

fig_affils.update_traces(textposition='outside')
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
    hover_data={"country": True, "truncated": False},
    color='total_citations',
    color_continuous_scale=px.colors.sequential.Magenta
)
fig_countries.update_layout(yaxis={'categoryorder': 'total ascending'})
fig_countries.show()