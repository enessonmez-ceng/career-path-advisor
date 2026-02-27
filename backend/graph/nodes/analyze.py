"""
Analyze Node
Analyzes skill gaps between current skills and target role requirements.
"""
from graph.state import CareerState, SkillLevel
from graph.chains.gap_analyzer import analyze_skill_gaps


def analyze_node(state: CareerState) -> dict:
    """
    Analyze the gap between current skills and target role requirements.
    
    Reads: current_skills, target_role, experiences
    Writes: skill_gaps, strengths, areas_to_improve
    """
    current_skills = state.get("current_skills", [])
    target_role = state.get("target_role") or "Not specified"
    experiences = state.get("experiences", [])
    
    # Extract skill names for the analyzer
    skill_names = [s.get("name", "") for s in current_skills if s.get("name")]
    
    # Build experience summary
    experience_summary = ""
    for exp in experiences:
        experience_summary += (
            f"- {exp.get('title', '')} at {exp.get('company', '')} "
            f"({exp.get('duration', '')})\n"
        )
    
    # Run the gap analysis
    gap_result = analyze_skill_gaps(
        current_skills=skill_names,
        target_role=target_role,
        experience_summary=experience_summary
    )
    
    # Convert gap items to state format
    level_map = {
        "beginner": SkillLevel.BEGINNER,
        "intermediate": SkillLevel.INTERMEDIATE,
        "advanced": SkillLevel.ADVANCED,
        "expert": SkillLevel.EXPERT,
    }
    
    skill_gaps = []
    for gap in gap_result.skill_gaps:
        skill_gaps.append({
            "skill": gap.skill,
            "current_level": level_map.get(
                gap.current_level.lower(), None
            ) if gap.current_level else None,
            "target_level": level_map.get(
                gap.target_level.lower(), SkillLevel.INTERMEDIATE
            ),
            "priority": gap.priority,
            "recommendation": gap.recommendation,
        })
    
    return {
        "skill_gaps": skill_gaps,
        "strengths": gap_result.strengths,
        "areas_to_improve": gap_result.areas_to_improve,
    }
