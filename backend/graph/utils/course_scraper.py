"""
Course Scraper
Scrapes courses from Udemy and Coursera using Scrapling.
"""
from typing import List
from datetime import datetime, timezone

from scrapling.fetchers import Fetcher


def scrape_udemy(keyword: str, max_results: int = 15) -> List[dict]:
    """
    Scrape free/popular courses from Udemy search.

    Args:
        keyword: Search term (e.g. "python", "react")
        max_results: Maximum courses to return

    Returns:
        List of opportunity dicts with type='course', source='udemy'
    """
    courses = []
    search_url = f"https://www.udemy.com/courses/search/?q={keyword}&sort=relevance"

    try:
        page = Fetcher.get(search_url, stealthy_headers=True)

        # Udemy course cards
        cards = page.css("div[data-purpose='course-card-container']")
        if not cards:
            # Fallback selector
            cards = page.css(".course-card--container--3w8Zm") or page.css("[class*='course-card']")

        for card in cards[:max_results]:
            try:
                title_el = card.css("h3") or card.css("[data-purpose='course-title-url'] a")
                title = title_el[0].text.strip() if title_el else ""

                link_el = card.css("a[href*='/course/']")
                href = link_el[0].attrib.get("href", "") if link_el else ""
                url = f"https://www.udemy.com{href}" if href and not href.startswith("http") else href

                instructor_el = card.css("[data-purpose='instructor-name']") or card.css("[class*='instructor']")
                instructor = instructor_el[0].text.strip() if instructor_el else "Udemy"

                desc_el = card.css("p") or card.css("[class*='description']")
                description = desc_el[0].text.strip() if desc_el else ""

                if title and url:
                    courses.append({
                        "type": "course",
                        "title": title,
                        "provider": instructor,
                        "url": url,
                        "description": description[:300],
                        "required_skills": [keyword],
                        "location": "Online",
                        "posted_date": "",
                        "source": "udemy",
                    })
            except Exception:
                continue

    except Exception as e:
        print(f"[Udemy] Scraping error: {e}")

    return courses


def scrape_coursera(keyword: str, max_results: int = 15) -> List[dict]:
    """
    Scrape courses from Coursera search.

    Args:
        keyword: Search term
        max_results: Maximum courses to return

    Returns:
        List of opportunity dicts with type='course', source='coursera'
    """
    courses = []
    search_url = f"https://www.coursera.org/search?query={keyword}"

    try:
        page = Fetcher.get(search_url, stealthy_headers=True)

        # Coursera result cards
        cards = page.css("li.cds-9") or page.css("[class*='result-']") or page.css("div[role='group'] > div")

        for card in cards[:max_results]:
            try:
                title_el = card.css("h3") or card.css("[class*='cardTitle']")
                title = title_el[0].text.strip() if title_el else ""

                link_el = card.css("a[href*='/learn/']") or card.css("a[href*='/specializations/']") or card.css("a")
                href = link_el[0].attrib.get("href", "") if link_el else ""
                url = f"https://www.coursera.org{href}" if href and not href.startswith("http") else href

                partner_el = card.css("[class*='partner']") or card.css("p")
                partner = partner_el[0].text.strip() if partner_el else "Coursera"

                desc_parts = card.css("span, p")
                description = " ".join([el.text.strip() for el in desc_parts[:2] if el.text.strip()])

                if title and url:
                    courses.append({
                        "type": "course",
                        "title": title,
                        "provider": partner,
                        "url": url,
                        "description": description[:300],
                        "required_skills": [keyword],
                        "location": "Online",
                        "posted_date": "",
                        "source": "coursera",
                    })
            except Exception:
                continue

    except Exception as e:
        print(f"[Coursera] Scraping error: {e}")

    return courses


def scrape_courses(keyword: str, max_per_source: int = 10) -> List[dict]:
    """
    Scrape courses from all supported platforms.

    Args:
        keyword: Search keyword
        max_per_source: Max results per platform

    Returns:
        Combined list from Udemy + Coursera
    """
    all_courses = []
    all_courses.extend(scrape_udemy(keyword, max_per_source))
    all_courses.extend(scrape_coursera(keyword, max_per_source))
    print(f"[Courses] Scraped {len(all_courses)} courses for '{keyword}'")
    return all_courses
