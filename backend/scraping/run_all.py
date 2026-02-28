"""
Run All Scrapers — Main Entry Point
Scrapes ALL internship/entry-level listings from LinkedIn using Bright Data
and stores them in Supabase with embedding vectors.

Usage:
    # Full live scraping (Bright Data API)
    python -m scraping.run_all

    # Only load static/curated data (no API calls)
    python -m scraping.run_all --static-only
"""
import argparse
import os
import sys

# Ensure backend/ is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from graph.utils.supabase_client import upsert_opportunities, get_stats


def load_static_data() -> list:
    """Load all static/curated data from field modules."""
    all_static = []

    try:
        from scraping.fields.computer_engineering import STATIC_DATA as CS
        all_static.extend(CS)
    except ImportError:
        pass

    try:
        from scraping.fields.electrical_engineering import STATIC_DATA as EE
        all_static.extend(EE)
    except ImportError:
        pass

    try:
        from scraping.fields.mechanical_engineering import STATIC_DATA as ME
        all_static.extend(ME)
    except ImportError:
        pass

    return all_static


def main():
    parser = argparse.ArgumentParser(
        description="Career Path Advisor — Bulk Internship Scraper"
    )
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Only load static/curated data (no Bright Data API calls).",
    )

    args = parser.parse_args()

    print("🚀 Career Path Advisor — Bulk Scraper")
    print("=" * 60)
    print(f"   Mode: {'Static Only' if args.static_only else '🌐 LIVE (Bright Data → LinkedIn)'}")
    print("=" * 60)

    all_opportunities = []

    if args.static_only:
        # ── Static data only ──
        static = load_static_data()
        print(f"\n📦 Loaded {len(static)} static records")
        all_opportunities = static
    else:
        # ── Live Bright Data scraping ──
        try:
            from scraping.base_scraper import BrightDataClient

            client = BrightDataClient()
            print("✅ Bright Data client initialized.\n")

            scraped = client.scrape_all_internships()
            all_opportunities.extend(scraped)

            # Also include static data as fallback
            static = load_static_data()
            # Only add static items whose URLs aren't already scraped
            scraped_urls = {o["url"] for o in scraped}
            new_static = [s for s in static if s["url"] not in scraped_urls]
            all_opportunities.extend(new_static)

            if new_static:
                print(f"\n📦 Added {len(new_static)} additional static records")

        except Exception as e:
            print(f"\n❌ Bright Data error: {e}")
            print("   Falling back to static data...")
            all_opportunities = load_static_data()

    # ── Upsert to Supabase (with auto embeddings) ──
    if all_opportunities:
        print(f"\n{'=' * 60}")
        print(f"💾 Upserting {len(all_opportunities)} opportunities to Supabase...")
        print(f"   (Generating embeddings for each — this may take a minute)")
        print(f"{'=' * 60}")

        try:
            upserted = upsert_opportunities(all_opportunities)
            print(f"\n✅ Upserted {upserted} rows with embeddings.")
        except Exception as e:
            print(f"\n❌ Supabase error: {e}")
    else:
        print("\n⚠️ No opportunities found.")

    # ── Stats ──
    try:
        stats = get_stats()
        print(f"\n{'=' * 60}")
        print(f"📈 Database Status")
        print(f"{'=' * 60}")
        print(f"  Total : {stats['total']}")
        print(f"  Active: {stats['active']}")
        for t, c in stats.get("by_type", {}).items():
            print(f"    {t:>15}: {c}")
    except Exception:
        pass

    print(f"\n✅ DONE!")


if __name__ == "__main__":
    main()
