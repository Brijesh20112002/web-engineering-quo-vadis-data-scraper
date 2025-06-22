# Trend-Wise
from collections import defaultdict

# Create a year-topic dictionary for citation and publication count
topic_stats_by_year = defaultdict(lambda: defaultdict(lambda: {"publications": 0, "citations": 0}))

# Iterate through each row
for _, row in df.iterrows():
    year = row["year"]
    citations = row["citations"] if pd.notnull(row["citations"]) else 0
    keywords = str(row["keywords"]).split(";")
    
    for kw in keywords:
        keyword = kw.strip().lower()
        if keyword:
            topic_stats_by_year[year][keyword]["publications"] += 1
            topic_stats_by_year[year][keyword]["citations"] += citations

# Convert to DataFrame for plotting (limit to top 5 topics by total publications)
topic_df = []

# First collect total publications across all years to find top topics
topic_totals = defaultdict(int)
for year, topics in topic_stats_by_year.items():
    for topic, stats in topics.items():
        topic_totals[topic] += stats["publications"]

# Get top 5 topics
top_topics = sorted(topic_totals.items(), key=lambda x: x[1], reverse=True)[:5]
top_topic_names = [t[0] for t in top_topics]

# Collect data only for top topics
for year, topics in topic_stats_by_year.items():
    for topic in top_topic_names:
        stats = topics.get(topic, {"publications": 0, "citations": 0})
        topic_df.append({
            "year": year,
            "topic": topic,
            "publications": stats["publications"],
            "citations": stats["citations"]
        })

topic_df = pd.DataFrame(topic_df)

# Plot topic trends
fig, ax = plt.subplots(2, 1, figsize=(12, 12), sharex=True)

# Publications by topic over time
sns.lineplot(data=topic_df, x="year", y="publications", hue="topic", marker="o", ax=ax[0])
ax[0].set_title("Publications per Topic Over Years")
ax[0].set_ylabel("Publications")

# Citations by topic over time
sns.lineplot(data=topic_df, x="year", y="citations", hue="topic", marker="o", ax=ax[1])
ax[1].set_title("Citations per Topic Over Years")
ax[1].set_ylabel("Citations")

plt.xlabel("Year")
plt.tight_layout()
plt.show()
