import pandas as pd

# Load both files
icwe_df = pd.read_csv("icwe_metadata_2019_2024.csv")   # Replace with your actual ICWE file path
jwe_df = pd.read_csv("JWE_metadata_2019_2024.csv")     # Replace with your actual JWE file path

# Normalize column names
icwe_df.columns = icwe_df.columns.str.strip().str.lower().str.replace(" ", "_")
jwe_df.columns = jwe_df.columns.str.strip().str.lower().str.replace(" ", "_")

# Rename JWE columns to match ICWE schema
jwe_df = jwe_df.rename(columns={
    "author": "authors",
    "affiliation": "affiliations",
    "author_keywords": "keywords",
    "citation_count": "citations",
    "page_number": "pages",
    "volume_number": "volume_number",
    "issue": "issue",
    "issue_identifier": "issue_name"
})

# Add missing fields to ICWE
icwe_df["track_or_issue_name"] = ""
icwe_df["volume_number"] = ""
icwe_df["issue"] = ""
icwe_df["issue_name"] = ""
icwe_df["length"] = icwe_df["pages"].astype(str).apply(lambda x: len(x.split('-')) if '-' in x else 1)

# Add missing fields to JWE
jwe_df["track_or_issue_name"] = jwe_df["issue_name"]
jwe_df["length"] = jwe_df["pages"].astype(str).apply(lambda x: len(x.split('-')) if '-' in x else 1)

# Define unified schema
common_columns = [
    "title", "authors", "affiliations", "keywords", "abstract", "venue", "year",
    "track_or_issue_name", "volume_number", "issue", "issue_name", "pages", "length",
    "citations", "url"
]

# Ensure all columns exist in both DataFrames
for col in common_columns:
    if col not in icwe_df.columns:
        icwe_df[col] = ""
    if col not in jwe_df.columns:
        jwe_df[col] = ""

# Reorder and trim both datasets
icwe_df = icwe_df[common_columns]
jwe_df = jwe_df[common_columns]

# Combine
combined_df = pd.concat([icwe_df, jwe_df], ignore_index=True)

# Save result
combined_df.to_csv("web_engineering_combined.csv", index=False)
print("✅ Combined CSV saved as: web_engineering_combined.csv")
