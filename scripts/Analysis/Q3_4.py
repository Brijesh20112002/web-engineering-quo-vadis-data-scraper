import numpy as np
import matplotlib.pyplot as plt

years = np.array([2019, 2020, 2021, 2022, 2023, 2024])
year_cols = [2019, 2020, 2021, 2022, 2023, 2024]

# Get top 10 topics
top10_df = topic_year_df.sort_values(by='Total', ascending=False).head(10)

topic_slopes = {}

plt.figure(figsize=(10, 6))
for topic in top10_df.index:
    y = top10_df.loc[topic, year_cols].values.astype(float)
    slope, intercept = np.polyfit(years, y, 1)
    topic_slopes[topic] = slope
    
    plt.plot(years, y, marker='o', label=f"{topic} (slope={slope:.2f})")

plt.title('Top 10 Topics Trend (2019-2024) with Slopes')
plt.xlabel('Year')
plt.ylabel('Count')
plt.grid(True)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Slope summary
print("\nTopic popularity trends (based on slope):\n")
for topic, slope in sorted(topic_slopes.items(), key=lambda x: -x[1]):
    trend = "gaining popularity" if slope > 0 else "losing popularity" if slope < 0 else "stable"
    print(f"{topic:25}: slope = {slope:.2f} → {trend}")


import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# === Load CSV ===
df = pd.read_csv('web_engineering_combined.csv')

# === Helper: extract countries from affiliation strings ===
def extract_countries(affiliations_str):
    if pd.isna(affiliations_str):
        return []
    affils = [a.strip() for a in affiliations_str.split(';') if a.strip()]
    countries = []
    for aff in affils:
        # crude rule: take last word as country if it looks like one
        parts = aff.split(',')
        last = parts[-1].strip()
        if len(last) >= 2:
            countries.append(last)
    return countries

# === Aggregate citations per country per year ===
country_citations = defaultdict(lambda: defaultdict(float))

for _, row in df.iterrows():
    year = int(row['year'])
    citations = float(row['citations']) if not pd.isna(row['citations']) else 0
    countries = extract_countries(row['affiliations'])
    if not countries:
        continue
    share = citations / len(countries)
    for country in countries:
        country_citations[country][year] += share

# === Find top 10 countries by total citations ===
total_citations_country = {c: sum(y.values()) for c, y in country_citations.items()}
top_countries = sorted(total_citations_country.items(), key=lambda x: x[1], reverse=True)[:10]
top_country_names = [c for c, _ in top_countries]

# === Build dataframe for plotting ===
years = sorted(df['year'].dropna().unique())
trend_data_country = {c: [country_citations[c].get(y, 0) for y in years] for c in top_country_names}
trend_df_country = pd.DataFrame(trend_data_country, index=years)

# === Compute slopes ===
slopes = {}
for country in trend_df_country.columns:
    x = np.array(years)
    y = np.array(trend_df_country[country])
    if len(x) >= 2:
        coeffs = np.polyfit(x, y, 1)  # linear fit: y = m*x + b
        slope = coeffs[0]
    else:
        slope = 0
    slopes[country] = slope

# === Plot ===
plt.figure(figsize=(12, 7))
for country in trend_df_country.columns:
    plt.plot(trend_df_country.index, trend_df_country[country], marker='o', label=f"{country} (slope={slopes[country]:.2f})")

plt.title('Top 10 Countries by Citations – Trends (2019–2024)')
plt.xlabel('Year')
plt.ylabel('Citations')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()

# === Show slopes sorted ===
print("\n📈 Citation trend slopes (citations per year):")
for c, s in sorted(slopes.items(), key=lambda x: x[1], reverse=True):
    print(f"{c}: {s:.2f}")


# First get the top 3 countries with positive slopes
top_positive_countries = [c for c, s in sorted(slopes.items(), key=lambda x: x[1], reverse=True) if s > 0][:3]

print(f"Top 3 countries with positive citation trend: {top_positive_countries}")

# For total citations
country_total_citations = {c: sum(trend_df_country[c]) for c in top_positive_countries}

print("\n📊 Total citations for these countries:")
for c in top_positive_countries:
    print(f"{c}: {country_total_citations[c]:.1f} citations")

# For top 3 most cited papers per country
for country in top_positive_countries:
    paper_citations = []
    for _, row in df.iterrows():
        citations = float(row['citations']) if not pd.isna(row['citations']) else 0
        year = int(row['year'])
        title = row['title']
        url = row['url'] if 'url' in row else ''
        countries = extract_countries(row['affiliations'])
        if country in countries:
            paper_citations.append({
                'title': title,
                'year': year,
                'citations': citations,
                'url': url
            })
    top_papers = sorted(paper_citations, key=lambda x: x['citations'], reverse=True)[:3]
    print(f"\n🏆 Top 3 papers for {country}:")
    for p in top_papers:
        print(f"- {p['title']} ({p['year']}) — {p['citations']} citations — {p['url']}")

