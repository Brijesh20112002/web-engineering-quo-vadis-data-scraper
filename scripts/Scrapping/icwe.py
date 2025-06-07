import requests
from bs4 import BeautifulSoup
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

SPRINGER_BASE_URL = "https://link.springer.com"
SERPAPI_KEY = "2e471cbb272e2d628b23ce609574f47e835a86b7330c3760bdf098a75e86a6bc"
SERPAPI_URL = "https://serpapi.com/search.json"

# Semaphore to limit concurrent SerpAPI calls (avoid rate limits)
serpapi_semaphore = threading.Semaphore(3)  # Max 3 concurrent calls to SerpAPI


def get_paper_links(volume_url):
    chapter_links = set()
    page_num = 1

    while True:
        url = volume_url if page_num == 1 else f"{volume_url}?page={page_num}#toc"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        toc_section = soup.find('section', attrs={'data-title': 'Table of contents'})
        if not toc_section:
            print(f"No TOC section found on page {page_num} of {volume_url}")
            break

        def find_chapter_links_in_list(ol):
            for li in ol.find_all('li', recursive=False):
                a_tags = li.find_all('a', href=True)
                for a in a_tags:
                    href = a['href']
                    if "/chapter/" in href:
                        full_url = href if href.startswith("http") else SPRINGER_BASE_URL + href
                        chapter_links.add(full_url)
                nested_ol = li.find('ol', recursive=False)
                if nested_ol:
                    find_chapter_links_in_list(nested_ol)

        top_ol = toc_section.find('ol')
        if top_ol:
            find_chapter_links_in_list(top_ol)
        else:
            print(f"No top-level <ol> found in TOC on page {page_num}")

        next_page_link = soup.find('a', {'rel': 'next'})
        if next_page_link:
            page_num += 1
            time.sleep(1)
        else:
            break

    return sorted(chapter_links)


def get_citation_count(doi=None, title=None):
    if not title:
        return "0"

    with serpapi_semaphore:
        params = {
            "engine": "google_scholar",
            "q": title,
            "api_key": SERPAPI_KEY
        }

        try:
            response = requests.get(SERPAPI_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "organic_results" in data and len(data["organic_results"]) > 0:
                result = data["organic_results"][0]
                try:
                    return str(result["inline_links"]["cited_by"]["total"])
                except KeyError:
                    return "0"
            return "0"
        except Exception as e:
            print(f"Warning: Could not fetch citation count for title='{title}'. Reason: {e}")
            return "0"


def parse_chapter_page(url, year):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    doi = url.split("/chapter/")[-1]

    title_tag = soup.find("h1", {"class": "ChapterTitle"}) or soup.find("h1", class_="c-article-title")
    title = title_tag.text.strip() if title_tag else ""

    author_affiliation_map = []
    ol = soup.find("ol", class_="c-article-author-affiliation__list")
    if ol:
        for li in ol.find_all("li"):
            aff = li.find("p", class_="c-article-author-affiliation__address")
            authors_p = li.find("p", class_="c-article-author-affiliation__authors-list")
            if aff and authors_p:
                affiliation = aff.get_text(strip=True)
                authors_html = authors_p.decode_contents().replace("&nbsp;", " ").replace("&amp;", "&")
                authors = [a.strip() for a in authors_html.split(" & ")]
                for author in authors:
                    author_affiliation_map.append((author, affiliation))

    authors = "; ".join([a for a, _ in author_affiliation_map])
    affiliations = "; ".join(list(set([aff for _, aff in author_affiliation_map])))

    # For 2024: if affiliations missing, set to "null"
    if year == 2024 and not affiliations.strip():
        affiliations = "null"

    keywords = []
    keyword_section = soup.find("ul", class_="c-article-subject-list") or soup.find("section", class_="c-article-subject-list")
    if keyword_section:
        keywords = [kw.text.strip() for kw in keyword_section.find_all("a")]

    # For 2024: if no keywords, set keywords to "null"
    if year == 2024 and len(keywords) == 0:
        keywords = ["null"]

    abstract = ""
    abstract_tag = soup.find("div", id="Abs1-content") or soup.find("section", {"class": "Abstract"})
    if abstract_tag:
        p = abstract_tag.find("p")
        if p:
            abstract = p.text.strip()

    venue = ""
    meta_venue_tags = [
        ("citation_journal_title", "Journal Title"),
        ("citation_conference_title", "Conference Title"),
        ("citation_book_title", "Book Title"),
    ]
    for meta_name, _ in meta_venue_tags:
        meta_tag = soup.find("meta", attrs={"name": meta_name})
        if meta_tag and meta_tag.has_attr("content"):
            venue = meta_tag["content"].strip()
            if venue:
                break
    if not venue:
        venue_tag = soup.find("span", class_="BookTitle")
        if venue_tag:
            venue = venue_tag.text.strip()
    if not venue:
        breadcrumb = soup.find("nav", {"aria-label": "breadcrumb"})
        if breadcrumb:
            parts = [a.text.strip() for a in breadcrumb.find_all("a")]
            if parts:
                venue = " > ".join(parts)

    year_str = ""
    year_tag = soup.find("span", class_="ArticleCitation_Year")
    if year_tag:
        year_str = year_tag.text.strip()
    else:
        meta_date = soup.find("meta", attrs={"name": "citation_publication_date"})
        if meta_date:
            year_str = meta_date['content'].split("-")[0]

    pages = ""
    meta_pages = soup.find("meta", attrs={"name": "citation_pages"})
    if meta_pages:
        pages = meta_pages['content']
    else:
        first = soup.find("meta", attrs={"name": "citation_firstpage"})
        last = soup.find("meta", attrs={"name": "citation_lastpage"})
        if first and last:
            pages = f"{first['content']}-{last['content']}"

    length = ""
    if pages and "-" in pages:
        try:
            start, end = pages.split("-")
            length = str(int(end) - int(start) + 1)
        except:
            length = ""

    citations = get_citation_count(doi=doi, title=title)

    # Removed the time.sleep here to speed things up with concurrency

    return {
        "title": title,
        "authors": authors,
        "affiliations": affiliations,
        "keywords": "; ".join(keywords),
        "abstract": abstract,
        "venue": venue,
        "year": year_str,
        "pages": pages,
        "length": length,
        "citations": citations,
        "url": url
    }


def scrape_icwe_metadata(years, output_csv):
    volume_suffix = {
        2019: "030-19274-7",
        2020: "030-50578-3",
        2021: "030-74296-6",
        2022: "031-09917-5",
        2023: "031-34444-2",
        2024: "031-62362-2"
    }

    all_papers = []

    for year in years:
        print(f"\n🔍 Scraping ICWE {year} proceedings...")
        volume_url = f"https://link.springer.com/book/10.1007/978-3-{volume_suffix[year]}"
        paper_links = get_paper_links(volume_url)
        print(f"✅ Found {len(paper_links)} papers in {year}\n")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(parse_chapter_page, url, year): url for url in paper_links}

            for i, future in enumerate(as_completed(futures), 1):
                paper_url = futures[future]
                try:
                    paper_metadata = future.result()
                    all_papers.append(paper_metadata)
                    print(f"📄 Scraped paper {i}/{len(paper_links)}: {paper_url}")
                except Exception as e:
                    print(f"⚠️ Failed to scrape {paper_url}: {e}")

    keys = all_papers[0].keys() if all_papers else []
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_papers)

    print(f"\n✅ Done! Saved {len(all_papers)} papers to {output_csv}")


if __name__ == "__main__":
    # Choose the years you want to scrape
    scrape_icwe_metadata(years=[2019, 2020, 2021, 2022, 2023, 2024], output_csv="icwe_metadata_2019-2024.csv")
