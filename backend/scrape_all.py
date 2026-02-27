"""
Scrape All — CLI Runner
Scrapes opportunities from all platforms and upserts to Supabase.

Usage:
    python scrape_all.py --target-role "Backend Developer" --location "Turkey"
    python scrape_all.py --target-role "Data Scientist" --max-jobs 10 --sources linkedin,udemy,coursera,indeed
"""
import argparse
import sys
import os

# Add backend to path so graph.utils imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from graph.utils.supabase_client import upsert_opportunities, get_stats
from graph.utils.job_scraper import scrape_linkedin_jobs
from graph.utils.course_scraper import scrape_udemy, scrape_coursera
from graph.utils.indeed_scraper import scrape_indeed


def run_scraping(
    target_role: str,
    location: str = "Turkey",
    max_per_source: int = 15,
    sources: list = None,
):
    """
    Run all scrapers and upsert results to Supabase.

    Args:
        target_role: The role to search for (e.g. "Backend Developer")
        location: Job location
        max_per_source: Max results per source
        sources: List of sources to scrape (default: all)
    """
    if sources is None:
        sources = ["linkedin", "udemy", "coursera", "indeed"]

    all_opportunities = []
    total_stats = {}

    # --- LinkedIn ---
    if "linkedin" in sources:
        print(f"\n{'='*50}")
        print(f"🔗 Scraping LinkedIn for '{target_role}' in {location}...")
        print(f"{'='*50}")
        try:
            linkedin_jobs = scrape_linkedin_jobs(target_role, location, max_per_source)
            all_opportunities.extend(linkedin_jobs)
            total_stats["linkedin"] = len(linkedin_jobs)
            print(f"✅ LinkedIn: {len(linkedin_jobs)} jobs found")
        except Exception as e:
            print(f"❌ LinkedIn error: {e}")
            total_stats["linkedin"] = 0

    # --- Indeed ---
    if "indeed" in sources:
        print(f"\n{'='*50}")
        print(f"🔍 Scraping Indeed for '{target_role}' in {location}...")
        print(f"{'='*50}")
        try:
            indeed_jobs = scrape_indeed(target_role, location, max_per_source)
            all_opportunities.extend(indeed_jobs)
            total_stats["indeed"] = len(indeed_jobs)
            print(f"✅ Indeed: {len(indeed_jobs)} jobs found")
        except Exception as e:
            print(f"❌ Indeed error: {e}")
            total_stats["indeed"] = 0

    # --- Udemy ---
    if "udemy" in sources:
        print(f"\n{'='*50}")
        print(f"📚 Scraping Udemy for '{target_role}' courses...")
        print(f"{'='*50}")
        try:
            udemy_courses = scrape_udemy(target_role, max_per_source)
            all_opportunities.extend(udemy_courses)
            total_stats["udemy"] = len(udemy_courses)
            print(f"✅ Udemy: {len(udemy_courses)} courses found")
        except Exception as e:
            print(f"❌ Udemy error: {e}")
            total_stats["udemy"] = 0

    # --- Coursera ---
    if "coursera" in sources:
        print(f"\n{'='*50}")
        print(f"🎓 Scraping Coursera for '{target_role}' courses...")
        print(f"{'='*50}")
        try:
            coursera_courses = scrape_coursera(target_role, max_per_source)
            all_opportunities.extend(coursera_courses)
            total_stats["coursera"] = len(coursera_courses)
            print(f"✅ Coursera: {len(coursera_courses)} courses found")
        except Exception as e:
            print(f"❌ Coursera error: {e}")
            total_stats["coursera"] = 0

    # --- Upsert to Supabase ---
    if all_opportunities:
        print(f"\n{'='*50}")
        print(f"💾 Upserting {len(all_opportunities)} opportunities to Supabase...")
        print(f"{'='*50}")
        try:
            upserted = upsert_opportunities(all_opportunities)
            print(f"✅ Upserted {upserted} rows to Supabase")
        except Exception as e:
            print(f"❌ Supabase upsert error: {e}")
    else:
        print("\n⚠️  No opportunities scraped from any source.")

    # --- Summary ---
    print(f"\n{'='*50}")
    print("📊 Scraping Summary")
    print(f"{'='*50}")
    for source, count in total_stats.items():
        emoji = "✅" if count > 0 else "❌"
        print(f"  {emoji} {source:>10}: {count} items")
    print(f"  {'─'*25}")
    print(f"  📦 Total scraped: {len(all_opportunities)}")

    # Show DB stats
    try:
        stats = get_stats()
        print(f"\n📈 Database Status:")
        print(f"  Total records: {stats['total']}")
        print(f"  Active: {stats['active']}")
        for src, cnt in stats.get("by_source", {}).items():
            print(f"    {src}: {cnt}")
    except Exception:
        pass

    return all_opportunities


def main():
    parser = argparse.ArgumentParser(
        description="Scrape career opportunities and store in Supabase"
    )
    parser.add_argument(
        "--target-role",
        type=str,
        required=True,
        help="Target job role (e.g. 'Backend Developer', 'Data Scientist')",
    )
    parser.add_argument(
        "--location",
        type=str,
        default="Turkey",
        help="Job location (default: Turkey)",
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=15,
        help="Max results per source (default: 15)",
    )
    parser.add_argument(
        "--sources",
        type=str,
        default="linkedin,udemy,coursera,indeed",
        help="Comma-separated sources (default: all)",
    )

    args = parser.parse_args()

    print(f"🚀 Career Path Advisor — Opportunity Scraper")
    print(f"   Role: {args.target_role}")
    print(f"   Location: {args.location}")
    print(f"   Sources: {args.sources}")
    print(f"   Max per source: {args.max_jobs}")

    sources = [s.strip() for s in args.sources.split(",")]

    run_scraping(
        target_role=args.target_role,
        location=args.location,
        max_per_source=args.max_jobs,
        sources=sources,
    )


if __name__ == "__main__":
    main()
