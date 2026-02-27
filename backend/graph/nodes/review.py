"""
Review Node
Implements the Reflection pattern — critiques and improves the draft report.
"""
from graph.state import CareerState
from graph.chains.reviewer import critique_report, revise_report


def review_node(state: CareerState) -> dict:
    """
    Review and improve the draft career report using the Reflection pattern.
    
    Reads: name, current_skills, target_role, skill_gaps,
           development_roadmap, draft_report,
           internship_recommendations, course_recommendations,
           event_recommendations, iteration
    Writes: critique, final_report, iteration
    """
    name = state.get("name", "Candidate")
    current_skills = state.get("current_skills", [])
    target_role = state.get("target_role", "Software Developer")
    skill_gaps = state.get("skill_gaps", [])
    draft_roadmap = state.get("development_roadmap", "")
    draft_report = state.get("draft_report", "")
    iteration = state.get("iteration", 0)
    
    # Extract names for the reviewer
    skill_names = [s.get("name", "") for s in current_skills if s.get("name")]
    gap_names = [g.get("skill", "") for g in skill_gaps if g.get("skill")]
    
    # Format recommendation titles for the reviewer
    internship_titles = [
        r.get("title", "") for r in state.get("internship_recommendations", [])
    ]
    course_titles = [
        r.get("title", "") for r in state.get("course_recommendations", [])
    ]
    event_titles = [
        r.get("title", "") for r in state.get("event_recommendations", [])
    ]
    
    # Step 1: Critique the draft
    review_result = critique_report(
        candidate_name=name,
        current_skills=skill_names,
        target_role=target_role,
        skill_gaps=gap_names,
        draft_roadmap=draft_roadmap,
        internship_recommendations=internship_titles,
        course_recommendations=course_titles,
        event_recommendations=event_titles,
    )
    
    # Format critique as string
    critique_text = f"## Review (Iteration {iteration + 1})\n\n"
    critique_text += f"**Overall Score:** {review_result.overall_score}/10\n\n"
    
    if review_result.strengths:
        critique_text += "**Strengths:**\n"
        for s in review_result.strengths:
            critique_text += f"- {s}\n"
        critique_text += "\n"
    
    if review_result.critiques:
        critique_text += "**Issues Found:**\n"
        for c in review_result.critiques:
            critique_text += (
                f"- [{c.severity.upper()}] {c.aspect}: {c.issue}\n"
                f"  → {c.suggestion}\n"
            )
        critique_text += "\n"
    
    new_iteration = iteration + 1
    
    # Step 2: If quality is sufficient or max iterations reached, finalize
    if review_result.overall_score >= 8 or not review_result.should_revise or new_iteration >= 3:
        return {
            "critique": critique_text,
            "final_report": draft_report,
            "iteration": new_iteration,
        }
    
    # Step 3: Revise the report based on critique
    revised = revise_report(
        draft_roadmap=draft_roadmap,
        draft_recommendations=draft_report,
        review_result=review_result,
    )
    
    # Build improved final report
    improved_report = draft_report + "\n\n---\n\n"
    improved_report += f"## Revised Roadmap (Iteration {new_iteration})\n\n"
    improved_report += revised.revised_roadmap + "\n\n"
    improved_report += revised.revised_recommendations + "\n\n"
    
    if revised.changes_made:
        improved_report += "### Changes Made\n"
        for change in revised.changes_made:
            improved_report += f"- {change}\n"
    
    return {
        "critique": critique_text,
        "final_report": improved_report,
        "development_roadmap": revised.revised_roadmap,
        "draft_report": improved_report,
        "iteration": new_iteration,
    }


def should_continue_review(state: CareerState) -> str:
    """
    Conditional edge: decide whether to continue reviewing or end.
    
    Returns:
        'generate' to loop back for another revision, or 'end' to finish
    """
    iteration = state.get("iteration", 0)
    final_report = state.get("final_report", "")
    
    # Stop if we have a final report and iteration >= 1, or max iterations reached
    if final_report and iteration >= 1:
        return "end"
    if iteration >= 3:
        return "end"
    
    return "generate"
