"""
LinkedIn Data Seeder
Loads LinkedIn CSV data (postings, job_skills, companies) into ChromaDB.

Usage:
    python seed_linkedin_data.py                # Full load
    python seed_linkedin_data.py --sample 50    # Load only 50 rows
    python seed_linkedin_data.py --no-embed     # Skip OpenAI embeddings (faster test)
"""
import argparse
import csv
import os
import sys
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_skills_mapping() -> dict:
    """Load skill abbreviation → full name mapping."""
    mapping = {}
    path = os.path.join(BASE_DIR, "mappings", "skills.csv")
    if not os.path.exists(path):
        print(f"[WARN] Skills mapping not found: {path}")
        return mapping

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["skill_abr"]] = row["skill_name"]

    print(f"[INFO] Loaded {len(mapping)} skill mappings")
    return mapping


def load_job_skills(limit: int = 0) -> dict:
    """Load job_id → list of skill abbreviations."""
    job_skills = {}
    path = os.path.join(BASE_DIR, "jobs", "job_skills.csv")
    if not os.path.exists(path):
        print(f"[WARN] Job skills not found: {path}")
        return job_skills

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jid = row.get("job_id", "")
            skill = row.get("skill_abr", "")
            if jid and skill:
                job_skills.setdefault(jid, []).append(skill)

    print(f"[INFO] Loaded skills for {len(job_skills)} jobs")
    return job_skills


def load_companies() -> dict:
    """Load company_id → company info dict."""
    companies = {}
    path = os.path.join(BASE_DIR, "companies", "companies.csv")
    if not os.path.exists(path):
        print(f"[WARN] Companies file not found: {path}")
        return companies

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get("company_id", "")
            if cid:
                companies[cid] = {
                    "name": row.get("name", ""),
                    "description": row.get("description", ""),
                    "city": row.get("city", ""),
                    "country": row.get("country", ""),
                    "url": row.get("url", ""),
                }

    print(f"[INFO] Loaded {len(companies)} companies")
    return companies


def seed_postings(sample: int = 0, skip_embeddings: bool = False):
    """
    Load postings.csv and seed into ChromaDB.

    Args:
        sample: If > 0, only load this many rows.
        skip_embeddings: If True, skip OpenAI embedding generation.
    """
    postings_path = os.path.join(BASE_DIR, "postings.csv")
    if not os.path.exists(postings_path):
        print(f"[ERROR] postings.csv not found at {postings_path}")
        return

    # Load supporting data
    skills_map = load_skills_mapping()
    job_skills = load_job_skills()
    companies = load_companies()

    # Temporarily override embedding if needed
    if skip_embeddings:
        from graph.utils import chromadb_client
        original_svc = chromadb_client._get_embedding_service

        def _mock_embedding_service():
            return {
                "embed": lambda item: None,
                "text": lambda item: original_svc()["text"](item),
            }

        chromadb_client._get_embedding_service = _mock_embedding_service
        print("[INFO] Embedding generation DISABLED (--no-embed)")

    from graph.utils.chromadb_client import upsert_opportunities

    # Parse postings
    items = []
    count = 0

    print(f"[INFO] Reading postings.csv...")
    with open(postings_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if sample and count >= sample:
                break

            job_id = row.get("job_id", "")
            title = row.get("title", "").strip()
            description = (row.get("description", "") or "").strip()[:500]
            company_name = row.get("company_name", "").strip()
            location = row.get("location", "").strip()
            url = row.get("job_posting_url", "").strip()
            listed_time = row.get("listed_time", "")
            experience_level = row.get("formatted_experience_level", "")
            work_type = row.get("formatted_work_type", "")

            if not title or not url:
                continue

            # Resolve skills
            skill_abrs = job_skills.get(job_id, [])
            resolved_skills = []
            for abr in skill_abrs:
                full_name = skills_map.get(abr, abr)
                resolved_skills.append(full_name)

            # Resolve company info
            company_id = row.get("company_id", "")
            company_info = companies.get(company_id, {})
            if not company_name and company_info:
                company_name = company_info.get("name", "")

            # Determine type
            opp_type = "job"
            if experience_level and "intern" in experience_level.lower():
                opp_type = "internship"
            elif experience_level and "entry" in experience_level.lower():
                opp_type = "entry_level"

            item = {
                "type": opp_type,
                "title": title,
                "provider": company_name or "Unknown",
                "url": url,
                "description": description,
                "required_skills": resolved_skills,
                "location": location,
                "posted_date": listed_time,
                "source": "linkedin",
            }

            items.append(item)
            count += 1

            # Upsert in batches of 50
            if len(items) >= 50:
                upserted = upsert_opportunities(items)
                print(f"  [BATCH] Upserted {upserted} items (total: {count})")
                items = []

    # Final batch
    if items:
        upserted = upsert_opportunities(items)
        print(f"  [BATCH] Upserted {upserted} items (total: {count})")

    print(f"\n[DONE] Seeded {count} postings into ChromaDB")

    # Print stats
    from graph.utils.chromadb_client import get_stats
    stats = get_stats()
    print(f"[STATS] {stats}")


def main():
    parser = argparse.ArgumentParser(description="Seed LinkedIn data into ChromaDB")
    parser.add_argument("--sample", type=int, default=0, help="Limit to N rows (0 = all)")
    parser.add_argument("--no-embed", action="store_true", help="Skip OpenAI embedding generation")
    args = parser.parse_args()

    start = time.time()
    seed_postings(sample=args.sample, skip_embeddings=args.no_embed)
    elapsed = time.time() - start
    print(f"\n[TIME] Completed in {elapsed:.1f} seconds")


if __name__ == "__main__":
    main()
