"""
Embedding Service
Generates vector embeddings using OpenAI's text-embedding-3-small model.
Used for:
  1. Encoding opportunity (title + description + skills) → vector
  2. Encoding user profile (skills + target_role + education) → vector
  3. Enabling cosine similarity search in ChromaDB
"""
import os
from typing import List, Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions, cheapest
EMBEDDING_DIMENSIONS = 1536

_openai_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """Get or create OpenAI client singleton."""
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY must be set in .env")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


# ═══════════════════════════════════════════════════════════
# Core Embedding Functions
# ═══════════════════════════════════════════════════════════

def generate_embedding(text: str) -> List[float]:
    """
    Generate a vector embedding for a given text.

    Args:
        text: Any text string to embed.

    Returns:
        List of 1536 floats (vector).
    """
    if not text or not text.strip():
        return []

    client = _get_client()
    response = client.embeddings.create(
        input=text.strip(),
        model=EMBEDDING_MODEL,
    )
    return response.data[0].embedding


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single API call.
    More efficient than calling generate_embedding() in a loop.

    Args:
        texts: List of text strings.

    Returns:
        List of embedding vectors (same order as input).
    """
    if not texts:
        return []

    # Filter out empty strings but track indices
    valid = [(i, t.strip()) for i, t in enumerate(texts) if t and t.strip()]
    if not valid:
        return [[] for _ in texts]

    client = _get_client()
    response = client.embeddings.create(
        input=[t for _, t in valid],
        model=EMBEDDING_MODEL,
    )

    # Map results back to original indices
    result = [[] for _ in texts]
    for (orig_idx, _), emb_data in zip(valid, response.data):
        result[orig_idx] = emb_data.embedding

    return result


# ═══════════════════════════════════════════════════════════
# Domain-Specific Embedding Functions
# ═══════════════════════════════════════════════════════════

def generate_opportunity_text(opportunity: dict) -> str:
    """
    Build a searchable text representation of an opportunity.
    Combines title, description, skills, and location.
    """
    parts = []

    title = opportunity.get("title", "")
    if title:
        parts.append(f"Title: {title}")

    provider = opportunity.get("provider", "")
    if provider:
        parts.append(f"Company: {provider}")

    desc = opportunity.get("description", "")
    if desc:
        parts.append(f"Description: {desc[:400]}")

    skills = opportunity.get("required_skills", [])
    if skills:
        if isinstance(skills, list):
            parts.append(f"Required Skills: {', '.join(skills)}")
        else:
            parts.append(f"Required Skills: {skills}")

    location = opportunity.get("location", "")
    if location:
        parts.append(f"Location: {location}")

    opp_type = opportunity.get("type", "")
    if opp_type:
        parts.append(f"Type: {opp_type}")

    return "\n".join(parts)


def generate_opportunity_embedding(opportunity: dict) -> List[float]:
    """
    Generate embedding for an opportunity (job/internship/course).

    Args:
        opportunity: Dict with title, description, required_skills, etc.

    Returns:
        1536-dimensional vector.
    """
    text = generate_opportunity_text(opportunity)
    return generate_embedding(text)


def generate_profile_embedding(
    skills: List[str],
    target_role: str = "",
    education_field: str = "",
    skill_gaps: List[str] = None,
) -> List[float]:
    """
    Generate embedding for a user profile.
    This vector is compared against opportunity embeddings for matching.

    Args:
        skills: User's current skills.
        target_role: Desired job role.
        education_field: Field of study.
        skill_gaps: Skills the user wants to develop.

    Returns:
        1536-dimensional vector.
    """
    parts = []

    if target_role:
        parts.append(f"Target Role: {target_role}")

    if skills:
        parts.append(f"Current Skills: {', '.join(skills)}")

    if education_field:
        parts.append(f"Education: {education_field}")

    if skill_gaps:
        parts.append(f"Skills to Learn: {', '.join(skill_gaps)}")

    text = "\n".join(parts)
    return generate_embedding(text)
