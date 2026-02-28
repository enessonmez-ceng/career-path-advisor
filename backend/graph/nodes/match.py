"""
Match Node
Re-scores and ranks all opportunities against the user profile.
"""
from graph.state import CareerState



async def match_node(state: CareerState) -> dict:
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
    
    # Run the custom hybrid matcher (0 API cost, explainable)
    from graph.utils.skill_matcher import rank_opportunities
    
    scored_opps = rank_opportunities(
        user_skills=skill_names,
        opportunities=all_opportunities,
        user_text=" ".join(strengths) if strengths else "",
    )
    
    # Build a lookup from matched results
    score_lookup = {}
    for opp in scored_opps:
        score_lookup[opp["title"]] = {
            "match_score": opp["match_score"],
            "reason": opp["match_explanation"],
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
