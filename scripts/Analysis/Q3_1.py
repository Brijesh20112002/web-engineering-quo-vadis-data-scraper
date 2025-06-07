import pandas as pd
import plotly.express as px

df = pd.read_csv('web_engineering_combined.csv')

df['year'] = pd.to_numeric(df['year'], errors='coerce')
df['citations'] = pd.to_numeric(df['citations'], errors='coerce')
df = df.dropna(subset=['year', 'citations'])

CURRENT_YEAR = 2025
df['age'] = CURRENT_YEAR - df['year']
df['age'] = df['age'].apply(lambda x: max(x, 1))

df['citations_per_year'] = df['citations'] / df['age']

top_articles = df.sort_values(by='citations_per_year', ascending=False).head(10).copy()

# Truncate titles to 50 characters for display
def truncate(text, max_len=50):
    return (text[:max_len] + '...') if len(text) > max_len else text

top_articles['title_trunc'] = top_articles['title'].apply(truncate)

# Compose hover text with full info
top_articles['hover'] = (
    'Title: ' + top_articles['title'] + '<br>' +
    'Authors: ' + top_articles['authors'] + '<br>' +
    'Year: ' + top_articles['year'].astype(str) + '<br>' +
    'Total Citations: ' + top_articles['citations'].astype(str) + '<br>' +
    'Citations per Year: ' + top_articles['citations_per_year'].round(2).astype(str)
)

fig = px.bar(
    top_articles,
    y='title_trunc',  # shorter titles on y-axis
    x='citations_per_year',
    orientation='h',
    hover_name='title',
    hover_data={'citations_per_year': ':.2f', 'year': True, 'authors': True, 'citations': True, 'title_trunc': False},
    labels={'citations_per_year': 'Citations per Year', 'title_trunc': 'Article Title'},
    title='Top 10 Most Cited Articles Relative to Their Age (Citations per Year)'
)

fig.update_layout(yaxis={'categoryorder':'total ascending'})
fig.show()
