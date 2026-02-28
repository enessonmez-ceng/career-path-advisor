"""
Bright Data Scraper — Bulk Internship Collector
Scrapes ALL internship/entry-level job listings from LinkedIn via Bright Data.
No field splitting, no artificial limits. Just get everything.

Usage:
    from scraping.base_scraper import BrightDataClient
    client = BrightDataClient()
    jobs = client.scrape_all_internships()
"""
import os
import time
import requests
from typing import List, Optional
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

# Bright Data LinkedIn Jobs dataset
LINKEDIN_DATASET_ID = "gd_lpfll7v5hcqtkxl6l"
API_BASE = "https://api.brightdata.com/datasets/v3"

# Broad search queries to capture ALL intern/entry-level listings
SEARCH_QUERIES = [
    ("intern", "Turkey"),
    ("stajyer", "Turkey"),
    ("staj", "Turkey"),
    ("new graduate", "Turkey"),
    ("junior developer", "Turkey"),
    ("junior engineer", "Turkey"),
    ("entry level engineer", "Turkey"),
    ("werkstudent", "Turkey"),
]


class BrightDataClient:
    """Client for Bright Data's Datasets API — bulk scraping."""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("BRIGHT_DATA_API_KEY", "")
        if not self.api_token:
            raise EnvironmentError(
                "BRIGHT_DATA_API_KEY must be set in .env file."
            )
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def scrape_all_internships(self) -> List[dict]:
        """
        Scrape ALL internship/entry-level listings from LinkedIn.
        Sends all search queries in one API call and collects all results.

        Returns:
            List of opportunity dicts ready for Supabase upsert.
        """
        # Build all search URLs
        input_urls = []
        for keyword, location in SEARCH_QUERIES:
            search_url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={keyword}&location={location}"
            )
            input_urls.append({"url": search_url})

        print(f"🔍 Sending {len(input_urls)} search queries to Bright Data...")
        for keyword, location in SEARCH_QUERIES:
            print(f"   • '{keyword}' in {location}")

        # Send ALL queries in one API call (discover_new mode)
        try:
            response = requests.post(
                f"{API_BASE}/scrape?dataset_id={LINKEDIN_DATASET_ID}"
                f"&notify=false&include_errors=true"
                f"&type=discover_new&discover_by=url",
                headers=self.headers,
                json={"input": input_urls},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

            snapshot_id = None
            if isinstance(data, dict):
                snapshot_id = data.get("snapshot_id")
            
            if not snapshot_id:
                print(f"   ⚠️ API response: {data}")
                return []

            print(f"\n⏳ Snapshot ID: {snapshot_id}")
            print(f"   Bright Data is processing. This may take a few minutes...")

            raw_results = self._poll_snapshot(snapshot_id)

        except requests.exceptions.RequestException as e:
            print(f"   ❌ API error: {e}")
            return []

        # Deduplicate and parse
        all_results = []
        seen_urls = set()

        for item in raw_results:
            opp = self._parse_linkedin_item(item, "search")
            if opp and opp["url"] not in seen_urls:
                seen_urls.add(opp["url"])
                all_results.append(opp)

        print(f"\n📊 Total unique listings collected: {len(all_results)}")
        return all_results

    def _scrape_linkedin_search(self, keyword: str, location: str) -> list:
        """Send a search query to Bright Data and return raw results."""
        try:
            response = requests.post(
                f"{API_BASE}/scrape?dataset_id={LINKEDIN_DATASET_ID}"
                f"&notify=false&include_errors=true",
                headers=self.headers,
                json={"input": [{"keyword": keyword, "location": location}]},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

            # Bright Data returns either immediate results or a snapshot_id
            if isinstance(data, list):
                print(f"   📦 Got {len(data)} results (immediate)")
                return data
            elif isinstance(data, dict):
                snapshot_id = data.get("snapshot_id")
                if snapshot_id:
                    print(f"   ⏳ Snapshot: {snapshot_id}, polling...")
                    return self._poll_snapshot(snapshot_id)
                else:
                    # Could be a status response or error
                    print(f"   ⚠️ API response: {data}")
                    return []
            else:
                return []

        except requests.exceptions.RequestException as e:
            print(f"   ❌ API error: {e}")
            return []

    def _poll_snapshot(
        self, snapshot_id: str, max_wait: int = 300, interval: int = 10
    ) -> list:
        """Poll Bright Data for completed snapshot results (handles JSON and NDJSON)."""
        import json as _json

        url = f"{API_BASE}/snapshot/{snapshot_id}?format=json"
        elapsed = 0

        while elapsed < max_wait:
            try:
                resp = requests.get(url, headers=self.headers, timeout=30)

                if resp.status_code == 200:
                    # Try standard JSON first
                    try:
                        data = resp.json()
                        if isinstance(data, list):
                            print(f"   📦 Snapshot ready: {len(data)} results")
                            return data
                    except Exception:
                        pass

                    # Fallback: NDJSON (newline-delimited JSON)
                    lines = [l for l in resp.text.strip().split("\n") if l.strip()]
                    results = []
                    for line in lines:
                        try:
                            item = _json.loads(line)
                            if isinstance(item, dict):
                                results.append(item)
                        except _json.JSONDecodeError:
                            continue

                    if results:
                        print(f"   📦 Snapshot ready: {len(results)} results (NDJSON)")
                        return results

                    return []
                elif resp.status_code == 202:
                    print(f"   ⏳ Processing... ({elapsed}s)")
                    time.sleep(interval)
                    elapsed += interval
                else:
                    print(f"   ❌ Snapshot error: {resp.status_code} - {resp.text[:200]}")
                    return []

            except requests.exceptions.RequestException as e:
                print(f"   ❌ Poll error: {e}")
                time.sleep(interval)
                elapsed += interval

        print("   ⏰ Polling timed out (5 min).")
        return []

    def _parse_linkedin_item(self, item: dict, search_keyword: str) -> Optional[dict]:
        """Convert a Bright Data LinkedIn result into an opportunity dict."""
        if not isinstance(item, dict):
            return None

        # Extract fields (Bright Data field names may vary)
        title = (
            item.get("title")
            or item.get("job_title")
            or item.get("name")
            or ""
        )
        company = (
            item.get("company")
            or item.get("company_name")
            or item.get("organization")
            or "Unknown"
        )
        job_url = (
            item.get("url")
            or item.get("job_url")
            or item.get("link")
            or ""
        )
        desc = (
            item.get("description")
            or item.get("job_description")
            or item.get("summary")
            or ""
        )
        location = (
            item.get("location")
            or item.get("job_location")
            or "Turkey"
        )
        posted = (
            item.get("date_posted")
            or item.get("posted_date")
            or item.get("posted_at")
            or ""
        )

        # Skills
        skills_raw = item.get("skills") or item.get("required_skills") or []
        if isinstance(skills_raw, str):
            skills_raw = [s.strip() for s in skills_raw.split(",") if s.strip()]

        # Skip if no title or URL
        if not title or not job_url:
            return None

        # Clean URL
        if "?" in job_url:
            job_url = job_url.split("?")[0]

        # Determine type (internship vs job)
        title_lower = title.lower()
        opp_type = "internship" if any(
            w in title_lower
            for w in ["intern", "staj", "stajyer", "trainee", "werkstudent", "co-op"]
        ) else "job"

        return {
            "type": opp_type,
            "title": title,
            "provider": company,
            "url": job_url,
            "description": (desc or "")[:500],
            "required_skills": skills_raw[:15],
            "location": location,
            "posted_date": posted,
            "source": "linkedin",
        }
