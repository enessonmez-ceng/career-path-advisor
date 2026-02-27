"""
Skill Database Utility
Loads and queries skills taxonomy and industry requirements from JSON files.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional


# Resolve paths relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"

_skills_taxonomy: Optional[Dict] = None
_industry_requirements: Optional[Dict] = None


def _load_json(file_path: Path) -> dict:
    """Load and parse a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_skills_taxonomy() -> Dict:
    """Get the full skills taxonomy. Cached after first load."""
    global _skills_taxonomy
    if _skills_taxonomy is None:
        _skills_taxonomy = _load_json(_DATA_DIR / "skills_taxonomy.json")
    return _skills_taxonomy


def get_industry_requirements() -> Dict:
    """Get the full industry requirements. Cached after first load."""
    global _industry_requirements
    if _industry_requirements is None:
        _industry_requirements = _load_json(_DATA_DIR / "industry_requirements.json")
    return _industry_requirements


def get_all_categories() -> List[str]:
    """Get all top-level skill categories (technical, soft, language, tool)."""
    taxonomy = get_skills_taxonomy()
    return list(taxonomy.get("categories", {}).keys())


def get_skills_by_category(category: str) -> list:
    """
    Get all skills in a specific category.
    
    Args:
        category: One of 'technical', 'soft', 'language', 'tool'
        
    Returns:
        List of skills (flat list for soft/language/tool, dict for technical)
    """
    taxonomy = get_skills_taxonomy()
    return taxonomy.get("categories", {}).get(category, [])


def get_technical_subcategories() -> List[str]:
    """Get all technical skill subcategories."""
    technical = get_skills_by_category("technical")
    if isinstance(technical, dict):
        return list(technical.keys())
    return []


def get_all_technical_skills() -> List[str]:
    """Get a flat list of all technical skills."""
    technical = get_skills_by_category("technical")
    if isinstance(technical, dict):
        all_skills = []
        for subcategory_skills in technical.values():
            all_skills.extend(subcategory_skills)
        return all_skills
    return technical if isinstance(technical, list) else []


def get_available_roles() -> List[str]:
    """Get all available role names from industry requirements."""
    requirements = get_industry_requirements()
    return list(requirements.get("roles", {}).keys())


def get_role_requirements(role: str) -> Optional[Dict]:
    """
    Get requirements for a specific role.
    
    Args:
        role: Role name (e.g., 'Backend Developer')
        
    Returns:
        Dict with description, required_skills, experience_levels or None
    """
    requirements = get_industry_requirements()
    return requirements.get("roles", {}).get(role)


def get_skills_for_role(role: str) -> Dict[str, List[str]]:
    """
    Get the required skills for a specific role.
    
    Args:
        role: Role name (e.g., 'Backend Developer')
        
    Returns:
        Dict with 'must_have', 'nice_to_have', 'soft_skills' lists
    """
    role_data = get_role_requirements(role)
    if role_data is None:
        return {"must_have": [], "nice_to_have": [], "soft_skills": []}
    return role_data.get("required_skills", {})


def find_matching_roles(skills: List[str], top_n: int = 3) -> List[Dict]:
    """
    Find roles that best match a given set of skills.
    
    Args:
        skills: List of skill names the user has
        top_n: Number of top matches to return
        
    Returns:
        List of dicts with 'role', 'match_count', 'total_required', 'match_percentage'
    """
    requirements = get_industry_requirements()
    skills_lower = {s.lower() for s in skills}
    
    matches = []
    for role_name, role_data in requirements.get("roles", {}).items():
        required = role_data.get("required_skills", {})
        must_have = [s.lower() for s in required.get("must_have", [])]
        nice_to_have = [s.lower() for s in required.get("nice_to_have", [])]
        all_required = must_have + nice_to_have
        
        match_count = sum(1 for s in all_required if s in skills_lower)
        total = len(all_required)
        
        matches.append({
            "role": role_name,
            "match_count": match_count,
            "total_required": total,
            "match_percentage": round(match_count / total * 100, 1) if total > 0 else 0
        })
    
    matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    return matches[:top_n]
