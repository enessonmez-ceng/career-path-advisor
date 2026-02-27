"""
Extract Node
Enriches raw skills with categories, levels, and experience estimates.
"""
from graph.state import CareerState
from graph.chains.skill_extractor import extract_and_enrich_skills, convert_to_state_skills


def extract_node(state: CareerState) -> dict:
    """
    Enrich raw skills from the parse step with detailed categorization.
    
    Reads: current_skills (raw), experiences
    Writes: current_skills (enriched with categories and levels)
    """
    raw_skills = state.get("current_skills", [])
    experiences = state.get("experiences", [])
    
    # Extract skill names from raw skills
    skill_names = [s.get("name", "") for s in raw_skills if s.get("name")]
    
    if not skill_names:
        return {"current_skills": []}
    
    # Build experience context string for better level estimation
    experience_context = ""
    for exp in experiences:
        experience_context += (
            f"- {exp.get('title', '')} at {exp.get('company', '')} "
            f"({exp.get('duration', '')}): {exp.get('description', '')}\n"
        )
    
    # Use skill extractor chain to enrich skills
    extraction_result = extract_and_enrich_skills(
        raw_skills=skill_names,
        experience_context=experience_context
    )
    
    # Convert to state-compatible format
    enriched_skills = convert_to_state_skills(extraction_result)
    
    return {"current_skills": enriched_skills}
