"""
ChromaDB Client Utility
Handles all ChromaDB operations: upsert, query, semantic search, and maintenance.
Replaces the old Supabase client with a local vector database.
"""
import os
import uuid
from typing import List, Optional
from datetime import datetime, timedelta, timezone

import chromadb
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


# ═══════════════════════════════════════════════════════════
# ChromaDB Client Singleton
# ═══════════════════════════════════════════════════════════

_chroma_client: Optional[chromadb.PersistentClient] = None
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")
COLLECTION_NAME = "opportunities"


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create a ChromaDB persistent client singleton."""
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _chroma_client


def get_collection() -> chromadb.Collection:
    """Get or create the opportunities collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


# ═══════════════════════════════════════════════════════════
# UPSERT
# ═══════════════════════════════════════════════════════════

def upsert_opportunities(items: List[dict]) -> int:
    """
    Bulk upsert opportunities to ChromaDB.
    Uses `url` as the unique ID to avoid duplicates.

    Args:
        items: List of dicts with keys: type, title, provider, url,
               description, required_skills, location, posted_date, source.

    Returns:
        Number of rows upserted.
    """
    if not items:
        return 0

    collection = get_collection()
    upserted_count = 0

    # Process in batches for efficiency
    batch_ids = []
    batch_docs = []
    batch_embeddings = []
    batch_metadatas = []

    for item in items:
        url = item.get("url", "")
        if not url:
            continue

        # Build a deterministic ID from URL
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, url))

        # Build metadata (ChromaDB metadata must be str/int/float/bool)
        skills = item.get("required_skills", [])
        if isinstance(skills, list):
            skills_str = ", ".join(skills)
        else:
            skills_str = str(skills)

        metadata = {
            "type": item.get("type", "job"),
            "title": item.get("title", ""),
            "provider": item.get("provider", "Unknown"),
            "url": url,
            "location": item.get("location", ""),
            "posted_date": item.get("posted_date", ""),
            "source": item.get("source", "manual"),
            "is_active": True,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "required_skills": skills_str,
        }

        # Build document text for ChromaDB's internal indexing
        svc = _get_embedding_service()
        doc_text = svc["text"](item)
        if not doc_text.strip():
            doc_text = item.get("title", "Untitled")

        # Generate embedding
        try:
            embedding = svc["embed"](item)
        except Exception as e:
            print(f"Embedding error for '{item.get('title', '')}': {e}")
            embedding = None

        batch_ids.append(doc_id)
        batch_docs.append(doc_text)
        batch_metadatas.append(metadata)
        if embedding:
            batch_embeddings.append(embedding)
        else:
            batch_embeddings.append(None)

    # Split into those with/without embeddings and upsert
    ids_with_emb = []
    docs_with_emb = []
    metas_with_emb = []
    embs_with_emb = []

    ids_no_emb = []
    docs_no_emb = []
    metas_no_emb = []

    for i in range(len(batch_ids)):
        if batch_embeddings[i] is not None:
            ids_with_emb.append(batch_ids[i])
            docs_with_emb.append(batch_docs[i])
            metas_with_emb.append(batch_metadatas[i])
            embs_with_emb.append(batch_embeddings[i])
        else:
            ids_no_emb.append(batch_ids[i])
            docs_no_emb.append(batch_docs[i])
            metas_no_emb.append(batch_metadatas[i])

    # Upsert in chunks of 100
    CHUNK = 100
    try:
        for start in range(0, len(ids_with_emb), CHUNK):
            end = start + CHUNK
            collection.upsert(
                ids=ids_with_emb[start:end],
                documents=docs_with_emb[start:end],
                metadatas=metas_with_emb[start:end],
                embeddings=embs_with_emb[start:end],
            )
        for start in range(0, len(ids_no_emb), CHUNK):
            end = start + CHUNK
            collection.upsert(
                ids=ids_no_emb[start:end],
                documents=docs_no_emb[start:end],
                metadatas=metas_no_emb[start:end],
            )
        upserted_count = len(batch_ids)
    except Exception as e:
        print(f"ChromaDB upsert error: {e}")

    return upserted_count


# ═══════════════════════════════════════════════════════════
# QUERY (metadata + keyword filtering)
# ═══════════════════════════════════════════════════════════

def query_opportunities(
    opp_type: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    source: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """
    Query opportunities from ChromaDB using metadata filters.

    Args:
        opp_type: Filter by type (job, internship, course, etc.)
        keywords: Text search keywords
        source: Filter by source
        limit: Max results

    Returns:
        List of opportunity dicts.
    """
    collection = get_collection()

    # Build metadata filter
    where_filters = [{"is_active": True}]
    if opp_type:
        where_filters.append({"type": opp_type})
    if source:
        where_filters.append({"source": source})

    where = {"$and": where_filters} if len(where_filters) > 1 else where_filters[0]

    # If keywords are provided, use them as query text for relevance
    if keywords:
        query_text = " ".join(keywords)
        try:
            results = collection.query(
                query_texts=[query_text],
                where=where,
                n_results=limit,
                include=["metadatas", "documents", "distances"],
            )
        except Exception as e:
            print(f"ChromaDB query error: {e}")
            return []
    else:
        # No keywords — just get by filter
        try:
            results = collection.get(
                where=where,
                limit=limit,
                include=["metadatas", "documents"],
            )
            # Normalize get() output to match query() shape
            results = {
                "ids": [results["ids"]],
                "metadatas": [results["metadatas"]],
                "documents": [results["documents"]],
                "distances": [None],
            }
        except Exception as e:
            print(f"ChromaDB get error: {e}")
            return []

    return _parse_results(results, keywords)


def _parse_results(results: dict, keywords: Optional[List[str]] = None) -> List[dict]:
    """Convert ChromaDB results to opportunity dicts."""
    opportunities = []

    ids_list = results.get("ids", [[]])[0] or []
    metas_list = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [None])[0]

    for i, meta in enumerate(metas_list):
        if not meta:
            continue

        skills_str = meta.get("required_skills", "")
        skills_list = [s.strip() for s in skills_str.split(",") if s.strip()] if skills_str else []

        # Cosine distance → similarity: similarity = 1 - distance
        similarity = 0.0
        if distances and i < len(distances):
            similarity = max(0.0, 1.0 - distances[i])

        opp = {
            "type": meta.get("type", "job"),
            "title": meta.get("title", ""),
            "provider": meta.get("provider", ""),
            "url": meta.get("url", ""),
            "description": "",  # stored in document text
            "required_skills": skills_list,
            "match_score": round(similarity, 3) if similarity else 0.0,
            "reason": f"From {meta.get('source', 'database')}",
            "location": meta.get("location", ""),
            "posted_date": meta.get("posted_date", ""),
        }
        opportunities.append(opp)

    # Simple keyword scoring fallback
    if keywords and opportunities:
        for opp in opportunities:
            text = f"{opp['title']} {opp.get('description', '')} {' '.join(opp['required_skills'])}".lower()
            hits = sum(1 for kw in keywords if kw.lower() in text)
            if hits > 0 and opp["match_score"] == 0.0:
                opp["match_score"] = min(hits / len(keywords), 1.0)

        opportunities.sort(key=lambda x: x["match_score"], reverse=True)

    return opportunities


# ═══════════════════════════════════════════════════════════
# SEMANTIC SEARCH (cosine similarity)
# ═══════════════════════════════════════════════════════════

def semantic_search(
    query_embedding: List[float],
    match_count: int = 20,
    match_threshold: float = 0.3,
    opp_type: Optional[str] = None,
) -> List[dict]:
    """
    Find the most similar opportunities using cosine similarity in ChromaDB.

    Args:
        query_embedding: 1536-dimensional embedding vector.
        match_count: Max results to return.
        match_threshold: Minimum cosine similarity (0.0-1.0).
        opp_type: Optional filter by type.

    Returns:
        List of opportunity dicts sorted by similarity (highest first).
    """
    collection = get_collection()

    # Build where filter
    where = {"is_active": True}
    if opp_type:
        where = {"$and": [{"is_active": True}, {"type": opp_type}]}

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            where=where,
            n_results=match_count,
            include=["metadatas", "documents", "distances"],
        )
    except Exception as e:
        print(f"ChromaDB semantic search error: {e}")
        return []

    opportunities = []

    ids_list = results.get("ids", [[]])[0] or []
    metas_list = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [None])[0] or []

    for i, meta in enumerate(metas_list):
        if not meta:
            continue

        # Cosine distance → similarity
        distance = distances[i] if i < len(distances) else 1.0
        similarity = max(0.0, 1.0 - distance)

        # Skip below threshold
        if similarity < match_threshold:
            continue

        skills_str = meta.get("required_skills", "")
        skills_list = [s.strip() for s in skills_str.split(",") if s.strip()] if skills_str else []

        opportunities.append({
            "type": meta.get("type", "job"),
            "title": meta.get("title", ""),
            "provider": meta.get("provider", ""),
            "url": meta.get("url", ""),
            "description": "",
            "required_skills": skills_list,
            "match_score": round(similarity, 3),
            "reason": f"Semantic match ({similarity:.0%} similarity)",
            "location": meta.get("location", ""),
            "posted_date": meta.get("posted_date", ""),
        })

    # Sort by similarity descending
    opportunities.sort(key=lambda x: x["match_score"], reverse=True)
    return opportunities


# ═══════════════════════════════════════════════════════════
# MAINTENANCE
# ═══════════════════════════════════════════════════════════

def deactivate_stale(days: int = 30) -> int:
    """
    Mark opportunities older than `days` as inactive.

    Returns:
        Number of rows deactivated.
    """
    collection = get_collection()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    try:
        # Get all active items
        results = collection.get(
            where={"is_active": True},
            include=["metadatas"],
        )

        stale_ids = []
        stale_metas = []
        for i, meta in enumerate(results["metadatas"] or []):
            scraped = meta.get("scraped_at", "")
            if scraped and scraped < cutoff:
                stale_ids.append(results["ids"][i])
                meta["is_active"] = False
                stale_metas.append(meta)

        if stale_ids:
            collection.update(
                ids=stale_ids,
                metadatas=stale_metas,
            )
        return len(stale_ids)
    except Exception as e:
        print(f"ChromaDB deactivate error: {e}")
        return 0


def get_stats() -> dict:
    """Get a summary of opportunities in the database."""
    collection = get_collection()

    try:
        results = collection.get(include=["metadatas"])
        metas = results.get("metadatas", []) or []
    except Exception as e:
        print(f"ChromaDB stats error: {e}")
        metas = []

    stats = {
        "total": len(metas),
        "active": sum(1 for m in metas if m.get("is_active")),
        "by_type": {},
        "by_source": {},
    }
    for m in metas:
        t = m.get("type", "unknown")
        s = m.get("source", "unknown")
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
        stats["by_source"][s] = stats["by_source"].get(s, 0) + 1

    return stats
