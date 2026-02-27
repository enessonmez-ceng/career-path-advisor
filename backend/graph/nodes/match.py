"""
Match Node
Re-scores and ranks all opportunities against the user profile.
"""
from graph.state import CareerState
from graph.chains.matcher import match_and_rank


def match_node(state: CareerState) -> dict:
    """
    Match and rank all gathered opportunities against the user profile.
    
    Reads: internship_recommendations, course_recommendations,
           event_recommendations, certification_recommendations,
           current_skills, target_role, skill_gaps, strengths
    Writes: updated recommendation lists with match scores
    """
    current_skills = state.get("current_skills", [])
    target_role = state.get("target_role", "Software Developer")
    skill_gaps = state.get("skill_gaps", [])
    strengths = state.get("strengths", [])
    
    # Extract names
    skill_names = [s.get("name", "") for s in current_skills if s.get("name")]
    gap_names = [g.get("skill", "") for g in skill_gaps if g.get("skill")]
    
    # Combine all opportunities
    all_opportunities = (
        state.get("internship_recommendations", [])
        + state.get("course_recommendations", [])
        + state.get("event_recommendations", [])
        + state.get("certification_recommendations", [])
    )
    
    if not all_opportunities:
        return {}
    
    # Run the matcher
    match_result = match_and_rank(
        opportunities=all_opportunities,
        current_skills=skill_names,
        target_role=target_role,
        skill_gaps=gap_names,
        strengths=strengths,
    )
    
    # Build a lookup from matched results
    score_lookup = {}
    for matched in match_result.matched_opportunities:
        score_lookup[matched.title] = {
            "match_score": matched.match_score,
            "reason": matched.reason,
        }
    
    # Update scores in each category
    def update_scores(recommendations: list) -> list:
        for rec in recommendations:
            title = rec.get("title", "")
            if title in score_lookup:
                rec["match_score"] = score_lookup[title]["match_score"]
                rec["reason"] = score_lookup[title]["reason"]
        # Sort by match_score descending
        return sorted(recommendations, key=lambda x: x.get("match_score", 0), reverse=True)
    
    return {
        "internship_recommendations": update_scores(state.get("internship_recommendations", [])),
        "course_recommendations": update_scores(state.get("course_recommendations", [])),
        "event_recommendations": update_scores(state.get("event_recommendations", [])),
        "certification_recommendations": update_scores(state.get("certification_recommendations", [])),
    }
