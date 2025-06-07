import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# API Keys
google_scholar_api_key = "2e471cbb272e2d628b23ce609574f47e835a86b7330c3760bdf098a75e86a6bc"
ieee_api_key = "f7c3tw77gv4c4cpxpnc6r8f4"

# Constants
YEARS = ["2019", "2020", "2021", "2022", "2023", "2024"]
google_scholar_api_url = "https://serpapi.com/search.json?engine=google_scholar"
publication_title = "Journal of Web Engineering"
issn = "1544-5976"
ieee_api_url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
max_records = 200
page_size = 200
csv_header = [
    "Venue", "Year", "Title", "Author", "Affiliation", "Country", "Author Keywords",
    "IEEE Keywords", "Volume Number", "Issue", "Issue Identifier", "Citation count",
    "URL", "Page number", "Abstract"
]

def get_country_from_address(address):
    if not address:
        return ""
    return address.split(",")[-1].strip()

def fetch_citation_count(doi):
    if not doi:
        return 0
    url = f"{google_scholar_api_url}&q={doi}&api_key={google_scholar_api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "organic_results" in data and data["organic_results"]:
                record = data["organic_results"][0]
                return record.get("inline_links", {}).get("cited_by", {}).get("total", 0)
        return 0
    except Exception as e:
        print(f"Error fetching citation count for DOI {doi}: {e}")
        return 0

def get_journal_publication_data(record_data, citation_count):
    year = record_data.get("publication_year", "")
    authornames = []
    affiliations = []
    countries = []

    authors = record_data.get("authors", {}).get("authors", [])
    for author in authors:
        name = author.get("full_name", "")
        affil = author.get("affiliation", "")
        authornames.append(name)
        affiliations.append(affil)
        country = get_country_from_address(affil)
        if country and country not in countries:
            countries.append(country)

    title = record_data.get("title", "")
    index_terms = record_data.get("index_terms", {})
    author_keywords = " | ".join(index_terms.get("author_terms", {}).get("terms", []))
    ieee_keywords = " | ".join(index_terms.get("ieee_terms", {}).get("terms", []))
    url = record_data.get("html_url", "")
    abstract = record_data.get("abstract", "")
    doi = record_data.get("doi", "")

    volume_number = record_data.get("volume", "")
    issue = record_data.get("issue", "")
    issue_identifier = record_data.get("issue_identifier", "") or record_data.get("issue_id", "")

    start_page = record_data.get("start_page", "")
    end_page = record_data.get("end_page", "")
    page_number = f"{start_page}-{end_page}" if start_page and end_page else ""

    return [
        "JWE", year, title,
        " | ".join(authornames),
        " | ".join(affiliations),
        " | ".join(countries),
        author_keywords,
        ieee_keywords,
        volume_number,
        issue,
        issue_identifier,
        citation_count,
        url,
        page_number,
        abstract
    ]

def scrape_journal_publications(year):
    data = []
    total_scraped = 0
    start_record = 1

    while True:
        url = (
            f"{ieee_api_url}?apikey={ieee_api_key}&publication_title={publication_title}"
            f"&issn={issn}&publication_year={year}&start_record={start_record}"
            f"&max_records={page_size}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Request failed for year {year}, start_record {start_record}, status code: {response.status_code}")
            break

        js = response.json()
        articles = js.get("articles", [])
        if not articles:
            break

        # Fetch citation counts in parallel
        doi_list = [article.get("doi", "") for article in articles]
        citation_map = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_doi = {executor.submit(fetch_citation_count, doi): doi for doi in doi_list}
            for future in as_completed(future_to_doi):
                doi = future_to_doi[future]
                citation_map[doi] = future.result()

        # Build records
        for article in articles:
            doi = article.get("doi", "")
            citation_count = citation_map.get(doi, 0)
            record = get_journal_publication_data(article, citation_count)
            data.append(record)
            total_scraped += 1

        print(f"Year {year} - Scraped {total_scraped} records so far...")
        start_record += page_size

        if total_scraped >= js.get("total_records", 0):
            break

    return data

def main():
    filename = "JWE_metadata_2019_2024.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(csv_header)

        for year in YEARS:
            print(f"Fetching records for year {year}")
            year_data = scrape_journal_publications(year)
            writer.writerows(year_data)

    print(f"\n✅ All data has been saved to {filename}")

if __name__ == "__main__":
    main()
