"""
Indeed Job Scraper
Scrapes job listings from Indeed using Scrapling.
"""
from typing import List
from datetime import datetime, timezone

from scrapling.fetchers import Fetcher


def scrape_indeed(
    keyword: str,
    location: str = "Turkey",
    max_results: int = 15
) -> List[dict]:
    """
    Scrape job listings from Indeed.

    Args:
        keyword: Job title / search term
        location: Location filter
        max_results: Maximum jobs to return

    Returns:
        List of opportunity dicts with type='internship'/'job', source='indeed'
    """
    jobs = []
    search_url = (
        f"https://www.indeed.com/jobs?q={keyword}&l={location}&sort=date"
    )

    try:
        page = Fetcher.get(search_url, stealthy_headers=True)

        # Indeed job cards
        cards = (
            page.css("div.job_seen_beacon")
            or page.css("[class*='jobsearch-ResultsList'] > li")
            or page.css("td.resultContent")
            or page.css("[class*='result']")
        )

        for card in cards[:max_results]:
            try:
                # Title
                title_el = (
                    card.css("h2.jobTitle a")
                    or card.css("[class*='jobTitle'] a")
                    or card.css("a[data-jk]")
                )
                title = title_el[0].text.strip() if title_el else ""

                # Link
                href = ""
                if title_el:
                    href = title_el[0].attrib.get("href", "")
                url = (
                    f"https://www.indeed.com{href}"
                    if href and not href.startswith("http")
                    else href
                )

                # Company
                company_el = (
                    card.css("[data-testid='company-name']")
                    or card.css("[class*='company']")
                    or card.css("span.companyName")
                )
                company = company_el[0].text.strip() if company_el else "Unknown"

                # Location
                loc_el = (
                    card.css("[data-testid='text-location']")
                    or card.css("[class*='companyLocation']")
                    or card.css("div.companyLocation")
                )
                job_location = loc_el[0].text.strip() if loc_el else location

                # Description snippet
                desc_el = (
                    card.css("div.job-snippet")
                    or card.css("[class*='job-snippet']")
                    or card.css("td.snip ul")
                )
                description = desc_el[0].text.strip() if desc_el else ""

                # Date
                date_el = (
                    card.css("span.date")
                    or card.css("[class*='date']")
                )
                posted = date_el[0].text.strip() if date_el else ""

                # Determine type
                opp_type = "internship" if "intern" in title.lower() else "job"

                if title and url:
                    jobs.append({
                        "type": opp_type,
                        "title": title,
                        "provider": company,
                        "url": url,
                        "description": description[:300],
                        "required_skills": [],
                        "location": job_location,
                        "posted_date": posted,
                        "source": "indeed",
                    })
            except Exception:
                continue

    except Exception as e:
        print(f"[Indeed] Scraping error: {e}")

    print(f"[Indeed] Scraped {len(jobs)} jobs for '{keyword}' in {location}")
    return jobs
