"""
Parse Node
Parses the uploaded CV document and extracts structured information.
"""
from graph.state import CareerState
from graph.chains.cv_parser import cv_parser_chain


def parse_node(state: CareerState) -> dict:
    """
    Parse the CV document content and extract structured information.
    
    Reads: document_content
    Writes: name, email, current_skills (raw), experiences, education
    """
    document_content = state.get("document_content", "")
    
    if not document_content:
        return {
            "name": "Unknown",
            "email": None,
            "current_skills": [],
            "experiences": [],
            "education": [],
        }
    
    # Use the CV parser chain to extract structured data
    parsed = cv_parser_chain.invoke({"cv_content": document_content})
    
    # Convert experiences to state format
    experiences = []
    for exp in parsed.experiences:
        experiences.append({
            "title": exp.title,
            "company": exp.company,
            "duration": exp.duration,
            "description": exp.description,
            "skills_used": exp.skills_used,
        })
    
    # Convert education to state format
    education = []
    for edu in parsed.education:
        education.append({
            "degree": edu.degree,
            "field": edu.field,
            "institution": edu.institution,
            "year": edu.year,
        })
    
    # Store raw skills as simple dicts (will be enriched in extract step)
    raw_skills = []
    for skill_name in parsed.skills:
        raw_skills.append({
            "name": skill_name,
            "category": "technical",  # placeholder, enriched later
            "level": "intermediate",  # placeholder, enriched later
            "years_experience": None,
        })
    
    return {
        "name": parsed.name,
        "email": parsed.email,
        "current_skills": raw_skills,
        "experiences": experiences,
        "education": education,
        "target_role": state.get("target_role") or parsed.inferred_target_role,
    }
