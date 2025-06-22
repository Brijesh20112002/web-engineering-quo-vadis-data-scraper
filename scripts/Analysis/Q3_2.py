import pandas as pd
import plotly.express as px
from collections import defaultdict

# Load data
df = pd.read_csv('web_engineering_combined.csv')

# Ensure citations are numeric and drop rows with missing citations
df['citations'] = pd.to_numeric(df['citations'], errors='coerce')
df = df.dropna(subset=['citations'])

# Function to parse keywords from string to list
def parse_keywords(text):
    if pd.isna(text):
        return []
    # Replace semicolons with commas, split, and strip whitespace
    return [k.strip() for k in text.replace(';', ',').split(',') if k.strip()]

df['keyword_list'] = df['keywords'].apply(parse_keywords)

# Calculate total citations per keyword
citations_per_keyword = defaultdict(float)

for _, row in df.iterrows():
    keywords = row['keyword_list']
    citations = row['citations']
    if keywords:
        share = citations / len(keywords)  # distribute citation count equally
        for kw in keywords:
            citations_per_keyword[kw] += share

# Convert to DataFrame
keyword_citations_df = pd.DataFrame(
    list(citations_per_keyword.items()),
    columns=['keyword', 'total_citations']
)

# Sort descending and take top 10
top_keywords = keyword_citations_df.sort_values(by='total_citations', ascending=False).head(10)

# Truncate long keyword names for better display
def truncate(text, max_length=30):
    return text if len(text) <= max_length else text[:max_length] + '...'

top_keywords['keyword_trunc'] = top_keywords['keyword'].apply(truncate)

# Plot the top 10 keywords with truncated names on y-axis
fig = px.bar(
    top_keywords,
    x='total_citations',
    y='keyword_trunc',
    orientation='h',
    title='Top 10 Topics (Areas) by Total Citations',
    labels={'total_citations': 'Total Citations', 'keyword_trunc': 'Topic/Keyword'},
    hover_data={'keyword': True, 'keyword_trunc': False},
    color='total_citations',
    color_continuous_scale=px.colors.sequential.Magenta
)

# Improve layout for readability
fig.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    height=600,
    margin=dict(l=200, r=50, t=50, b=50)  # left margin to fit longer labels
)

fig.show()
