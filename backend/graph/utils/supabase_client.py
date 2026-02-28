"""
Supabase Client Utility
Handles all Supabase operations: upsert, query, semantic search, and maintenance.
"""
import os
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Lazy import to avoid circular deps
_embedding_service = None

def _get_embedding_service():
    """Lazy-load embedding service."""
    global _embedding_service
    if _embedding_service is None:
        from graph.utils.embedding_service import (
            generate_opportunity_embedding,
            generate_opportunity_text,
        )
        _embedding_service = {
            "embed": generate_opportunity_embedding,
            "text": generate_opportunity_text,
        }
    return _embedding_service

_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create a Supabase client singleton."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise EnvironmentError(
                "SUPABASE_URL and SUPABASE_KEY must be set in .env"
            )
        _client = create_client(url, key)
    return _client


def _upsert_provider(client: Client, provider_name: str) -> Optional[str]:
    """Ensures provider exists and returns its ID."""
    if not provider_name:
        return None
    try:
        # Try to get existing
        res = client.table("providers").select("id").eq("name", provider_name).execute()
        if res.data:
            return res.data[0]["id"]
        
        # Insert new
        res = client.table("providers").insert({"name": provider_name}).execute()
        if res.data:
            return res.data[0]["id"]
    except Exception as e:
        print(f"Error upserting provider '{provider_name}': {e}")
    return None


def _upsert_skill(client: Client, skill_name: str) -> Optional[str]:
    """Ensures skill exists and returns its ID."""
    if not skill_name:
        return None
    try:
        res = client.table("skills").select("id").eq("name", skill_name).execute()
        if res.data:
            return res.data[0]["id"]
            
        res = client.table("skills").insert({"name": skill_name}).execute()
        if res.data:
            return res.data[0]["id"]
    except Exception as e:
        print(f"Error upserting skill '{skill_name}': {e}")
    return None


def upsert_opportunities(items: List[dict]) -> int:
    """
    Bulk upsert opportunities to Supabase (3NF compliant).
    Uses `url` as the conflict key to avoid duplicates.

    Args:
        items: List of dicts with keys matching the opportunities table.

    Returns:
        Number of rows upserted into opportunities.
    """
    if not items:
        return 0

    client = get_supabase_client()
    upserted_count = 0

    for item in items:
        # Skip empty URLs (can't upsert without unique key)
        url = item.get("url", "")
        if not url:
            continue

        # 1. Upsert Provider
        provider_name = item.get("provider", "Unknown")
        provider_id = _upsert_provider(client, provider_name)

        # 2. Upsert Opportunity
        opp_row = {
            "type": item.get("type", "job"),
            "title": item.get("title", ""),
            "provider_id": provider_id,
            "url": url,
            "description": (item.get("description", "") or "")[:500],
            "location": item.get("location", ""),
            "posted_date": item.get("posted_date", ""),
            "source": item.get("source", "manual"),
            "is_active": True,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

        # 2b. Generate embedding vector
        try:
            svc = _get_embedding_service()
            embedding = svc["embed"](item)
            if embedding:
                opp_row["embedding"] = embedding
        except Exception as e:
            print(f"Embedding error for '{item.get('title', '')}': {e}")

        try:
            # Upsert opportunity to get opportunity_id
            opp_res = client.table("opportunities").upsert(opp_row, on_conflict="url").execute()
            
            if opp_res.data:
                opp_id = opp_res.data[0]["id"]
                upserted_count += 1
                
                # 3. Handle Skills (N:M relation)
                req_skills = item.get("required_skills", [])
                for skill in set(req_skills):  # Use set to avoid duplicates
                    skill_id = _upsert_skill(client, skill)
                    if skill_id:
                        try:
                            client.table("opportunity_skills").upsert({
                                "opportunity_id": opp_id,
                                "skill_id": skill_id
                            }).execute()
                        except Exception:
                            pass # Already linked
        except Exception as e:
            print(f"Error upserting opportunity '{url}': {e}")

    return upserted_count


def query_opportunities(
    opp_type: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    source: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """
    Query opportunities from Supabase and un-normalize back to simple dicts.
    Fetches related Provider and Skills via join syntax.

    Args:
        opp_type: Filter by type
        keywords: Text search keywords
        source: Filter by source
        limit: Max results

    Returns:
        List of opportunity dicts matching the old interface.
    """
    client = get_supabase_client()
    
    # Use Supabase nested select to fetch relations
    query = client.table("opportunities").select(
        "*, providers(name), opportunity_skills(skills(name))"
    ).eq("is_active", True)

    if opp_type:
        query = query.eq("type", opp_type)
    if source:
        query = query.eq("source", source)

    query = query.order("scraped_at", desc=True).limit(limit)
    result = query.execute()

    opportunities = []
    for row in result.data or []:
        # Extract Provider name
        provider_name = ""
        pd = row.get("providers")
        if isinstance(pd, dict):
             provider_name = pd.get("name", "")

        # Extract Skills list
        extracted_skills = []
        os_list = row.get("opportunity_skills", [])
        if isinstance(os_list, list):
            for entry in os_list:
                sk = entry.get("skills")
                if isinstance(sk, dict) and sk.get("name"):
                    extracted_skills.append(sk["name"])

        opportunities.append({
            "type": row.get("type", "job"),
            "title": row.get("title", ""),
            "provider": provider_name,
            "url": row.get("url", ""),
            "description": row.get("description", ""),
            "required_skills": extracted_skills,
            "match_score": 0.0,
            "reason": f"From {row.get('source', 'database')}",
            "location": row.get("location", ""),
            "posted_date": row.get("posted_date", ""),
        })

    # Simple keyword filtering if provided
    if keywords and opportunities:
        scored = []
        for opp in opportunities:
            text = f"{opp['title']} {opp['description']}".lower()
            hits = sum(1 for kw in keywords if kw.lower() in text)
            if hits > 0:
                opp["match_score"] = min(hits / len(keywords), 1.0)
                scored.append(opp)
        
        # Return keyword-matched first, then remaining
        scored.sort(key=lambda x: x["match_score"], reverse=True)
        remaining = [o for o in opportunities if o not in scored]
        opportunities = scored + remaining

    return opportunities[:limit]


def deactivate_stale(days: int = 30) -> int:
    """
    Mark opportunities older than `days` as inactive.

    Returns:
        Number of rows deactivated.
    """
    client = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    result = (
        client.table("opportunities")
        .update({"is_active": False})
        .lt("scraped_at", cutoff)
        .eq("is_active", True)
        .execute()
    )
    return len(result.data) if result.data else 0


def get_stats() -> dict:
    """Get a summary of opportunities in the database."""
    client = get_supabase_client()

    result = client.table("opportunities").select("type, source, is_active").execute()
    rows = result.data or []

    stats = {
        "total": len(rows),
        "active": sum(1 for r in rows if r.get("is_active")),
        "by_type": {},
        "by_source": {},
    }
    for r in rows:
        t = r.get("type", "unknown")
        s = r.get("source", "unknown")
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
        stats["by_source"][s] = stats["by_source"].get(s, 0) + 1

    return stats


# ═══════════════════════════════════════════════════════════
# SEMANTIC SEARCH (pgvector)
# ═══════════════════════════════════════════════════════════

def semantic_search(
    query_embedding: List[float],
    match_count: int = 20,
    match_threshold: float = 0.3,
    opp_type: Optional[str] = None,
) -> List[dict]:
    """
    Find the most similar opportunities to a query embedding using pgvector.

    Args:
        query_embedding: 1536-dimensional embedding vector.
        match_count: Max results to return.
        match_threshold: Minimum cosine similarity (0.0-1.0).
        opp_type: Optional filter by type ("internship", "course", etc.).

    Returns:
        List of opportunity dicts sorted by similarity (highest first).
    """
    client = get_supabase_client()

    # Call the SQL function we created in Supabase
    result = client.rpc(
        "match_opportunities",
        {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
        },
    ).execute()

    if not result.data:
        return []

    opportunities = []
    for row in result.data:
        # Optionally filter by type
        if opp_type and row.get("type") != opp_type:
            continue

        # Fetch provider name
        provider_name = ""
        pid = row.get("provider_id")
        if pid:
            try:
                pr = client.table("providers").select("name").eq("id", pid).execute()
                if pr.data:
                    provider_name = pr.data[0].get("name", "")
            except Exception:
                pass

        # Fetch skills
        skills = []
        oid = row.get("id")
        if oid:
            try:
                sk = client.table("opportunity_skills").select(
                    "skills(name)"
                ).eq("opportunity_id", oid).execute()
                for s in (sk.data or []):
                    skill_data = s.get("skills")
                    if isinstance(skill_data, dict) and skill_data.get("name"):
                        skills.append(skill_data["name"])
            except Exception:
                pass

        similarity = row.get("similarity", 0.0)

        opportunities.append({
            "type": row.get("type", "job"),
            "title": row.get("title", ""),
            "provider": provider_name,
            "url": row.get("url", ""),
            "description": row.get("description", ""),
            "required_skills": skills,
            "match_score": round(similarity, 3),
            "reason": f"Semantic match ({similarity:.0%} similarity)",
            "location": row.get("location", ""),
            "posted_date": row.get("posted_date", ""),
        })

    return opportunities
