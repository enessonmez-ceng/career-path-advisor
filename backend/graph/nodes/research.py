"""
Research Node
Searches for internships, courses, events, and certifications.
"""
from graph.state import CareerState
from graph.chains.opportunity_researcher import research_opportunities


async def research_node(state: CareerState) -> dict:
    """
    Research opportunities based on user skills and identified gaps.
    
    Reads: current_skills, target_role, skill_gaps
    Writes: internship_recommendations, course_recommendations,
            event_recommendations, certification_recommendations
    """
    current_skills = state.get("current_skills", [])
    target_role = state.get("target_role", "Software Developer")
    skill_gaps = state.get("skill_gaps", [])
    
    # Extract skill names
    skill_names = [s.get("name", "") for s in current_skills if s.get("name")]
    
    # Extract gap skill names
    gap_names = [g.get("skill", "") for g in skill_gaps if g.get("skill")]
    
    # Research all types of opportunities
    results = research_opportunities(
        current_skills=skill_names,
        target_role=target_role,
        skill_gaps=gap_names,
        location="Turkey",
        use_tavily=True,
    )
    
    return {
        "internship_recommendations": results.get("internships", []),
        "course_recommendations": results.get("courses", []),
        "event_recommendations": results.get("events", []),
        "certification_recommendations": results.get("certifications", []),
    }
