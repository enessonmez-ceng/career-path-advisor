"""
LinkedIn Jobs Scraper
Scrapes job postings from LinkedIn using Scrapling.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional
import time
import random
import json
from datetime import datetime, timezone
from urllib.parse import quote

from scrapling.fetchers import Fetcher


@dataclass
class JobData:
    """Raw job data from LinkedIn scraping"""
    title: str
    company: str
    location: str
    job_link: str
    posted_date: str
    description: str = ""
    required_skills: List[str] = None

    def __post_init__(self):
        if self.required_skills is None:
            self.required_skills = []

    def to_opportunity(self, match_score: float = 0.0, reason: str = "") -> dict:
        """Convert to Opportunity format compatible with CareerState."""
        return {
            "type": "internship",
            "title": self.title,
            "provider": self.company,
            "url": self.job_link,
            "description": self.description or f"{self.title} at {self.company} - {self.location}",
            "required_skills": self.required_skills,
            "match_score": match_score,
            "reason": reason,
            "location": self.location,
            "posted_date": self.posted_date,
            "source": "linkedin",
        }

    def to_supabase_row(self) -> dict:
        """Convert to Supabase-ready row format"""
        return {
            "type": "internship",
            "title": self.title,
            "provider": self.company,
            "url": self.job_link,
            "description": self.description,
            "required_skills": self.required_skills,
            "location": self.location,
            "posted_date": self.posted_date,
            "source": "linkedin",
            "is_active": True,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }


class ScraperConfig:
    """Configuration for LinkedIn scraping"""
    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    JOBS_PER_PAGE = 25
    MIN_DELAY = 2
    MAX_DELAY = 5


class LinkedInJobsScraper:
    """Scraper for LinkedIn job postings using Scrapling"""

    def _build_search_url(self, keywords: str, location: str, start: int = 0) -> str:
        params = {
            "keywords": keywords,
            "location": location,
            "start": start,
        }
        return f"{ScraperConfig.BASE_URL}?{'&'.join(f'{k}={quote(str(v))}' for k, v in params.items())}"

    def _extract_job_data(self, card) -> Optional[JobData]:
        """Extract job data from a Scrapling element."""
        try:
            title_el = card.css("h3.base-search-card__title")
            title = title_el[0].text.strip() if title_el else ""

            company_el = card.css("h4.base-search-card__subtitle")
            company = company_el[0].text.strip() if company_el else ""

            loc_el = card.css("span.job-search-card__location")
            location = loc_el[0].text.strip() if loc_el else ""

            link_el = card.css("a.base-card__full-link")
            href = link_el[0].attrib.get("href", "") if link_el else ""
            job_link = href.split("?")[0] if "?" in href else href

            date_el = card.css("time.job-search-card__listdate")
            posted_date = date_el[0].text.strip() if date_el else "N/A"

            if title and job_link:
                return JobData(
                    title=title,
                    company=company,
                    location=location,
                    job_link=job_link,
                    posted_date=posted_date,
                )
        except Exception as e:
            print(f"Failed to extract job data: {e}")
        return None

    def scrape_jobs(
        self,
        keywords: str,
        location: str,
        max_jobs: int = 100,
    ) -> List[JobData]:
        """
        Scrape job listings from LinkedIn.

        Args:
            keywords: Search keywords (e.g. "Software Engineer Intern")
            location: Location (e.g. "Istanbul, Turkey")
            max_jobs: Maximum number of jobs to scrape

        Returns:
            List of JobData objects
        """
        all_jobs = []
        start = 0

        while len(all_jobs) < max_jobs:
            try:
                url = self._build_search_url(keywords, location, start)
                page = Fetcher.get(url, stealthy_headers=True)

                cards = page.css("div.base-card") or page.css("[class*='base-card']")

                if not cards:
                    break

                for card in cards:
                    job = self._extract_job_data(card)
                    if job:
                        all_jobs.append(job)
                        if len(all_jobs) >= max_jobs:
                            break

                print(f"[LinkedIn] Scraped {len(all_jobs)} jobs...")
                start += ScraperConfig.JOBS_PER_PAGE

                time.sleep(random.uniform(ScraperConfig.MIN_DELAY, ScraperConfig.MAX_DELAY))

            except Exception as e:
                print(f"[LinkedIn] Scraping error: {e}")
                break

        return all_jobs[:max_jobs]

    def get_opportunities(self, jobs: List[JobData]) -> List[dict]:
        """Convert scraped jobs to Opportunity format."""
        return [job.to_opportunity() for job in jobs]

    def get_supabase_rows(self, jobs: List[JobData]) -> List[dict]:
        """Convert scraped jobs to Supabase row format."""
        return [job.to_supabase_row() for job in jobs]


# Convenience functions
def scrape_linkedin_jobs(
    keyword: str, location: str = "Turkey", max_jobs: int = 25
) -> List[dict]:
    """Scrape LinkedIn jobs and return as opportunity dicts."""
    scraper = LinkedInJobsScraper()
    jobs = scraper.scrape_jobs(keyword, location, max_jobs)
    return scraper.get_opportunities(jobs)