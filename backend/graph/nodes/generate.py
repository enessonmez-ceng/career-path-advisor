"""
Generate Node
Creates the development roadmap and draft career report.
"""
from graph.state import CareerState
from graph.chains.roadmap_gen import create_roadmap


def generate_node(state: CareerState) -> dict:
    """
    Generate a development roadmap and compile the draft career report.
    
    Reads: skill_gaps, current_skills, target_role, name,
           internship_recommendations, course_recommendations,
           event_recommendations, certification_recommendations,
           strengths, areas_to_improve, education, experiences
    Writes: development_roadmap, draft_report
    """
    skill_gaps = state.get("skill_gaps", [])
    current_skills = state.get("current_skills", [])
    target_role = state.get("target_role", "Software Developer")
    name = state.get("name", "Candidate")
    
    # Extract skill names
    skill_names = [s.get("name", "") for s in current_skills if s.get("name")]
    gap_names = [g.get("skill", "") for g in skill_gaps if g.get("skill")]
    
    # Generate roadmap using the roadmap chain
    roadmap = create_roadmap(
        targeted_skills=gap_names,
        known_skills=skill_names,
    )
    
    # Format the roadmap as a readable string
    roadmap_text = f"## Learning Roadmap\n\n"
    roadmap_text += f"**Recommended Hours per Week:** {roadmap.hours_per_week}\n\n"
    
    for i, step in enumerate(roadmap.steps, 1):
        if hasattr(step, "target_skill"):
            # Course step
            roadmap_text += (
                f"### Step {i}: Learn {step.target_skill}\n"
                f"- **Resource:** {step.resource}\n"
                f"- **Duration:** {step.possible_duration}\n\n"
            )
        elif hasattr(step, "skills_required"):
            # Project step
            roadmap_text += (
                f"### Step {i}: Practice Project\n"
                f"- **Skills:** {', '.join(step.skills_required)}\n"
                f"- **Duration:** {step.possible_duration}\n"
                f"- **Benefits:** {step.potential_profits}\n\n"
            )
    
    # Compile the draft report
    internships = state.get("internship_recommendations", [])
    courses = state.get("course_recommendations", [])
    events = state.get("event_recommendations", [])
    certs = state.get("certification_recommendations", [])
    strengths = state.get("strengths", [])
    areas = state.get("areas_to_improve", [])
    
    draft_report = f"# Career Development Report for {name}\n\n"
    draft_report += f"**Target Role:** {target_role}\n\n"
    
    # Profile summary
    draft_report += "## Profile Summary\n\n"
    draft_report += f"**Current Skills:** {', '.join(skill_names)}\n\n"
    
    if strengths:
        draft_report += "**Strengths:**\n"
        for s in strengths:
            draft_report += f"- {s}\n"
        draft_report += "\n"
    
    if areas:
        draft_report += "**Areas to Improve:**\n"
        for a in areas:
            draft_report += f"- {a}\n"
        draft_report += "\n"
    
    # Skill gaps
    if skill_gaps:
        draft_report += "## Skill Gap Analysis\n\n"
        for gap in skill_gaps:
            draft_report += (
                f"- **{gap.get('skill', '')}** "
                f"[Priority: {gap.get('priority', 'medium')}] — "
                f"{gap.get('recommendation', '')}\n"
            )
        draft_report += "\n"
    
    # Recommendations
    def format_recommendations(title: str, recs: list) -> str:
        if not recs:
            return ""
        text = f"## {title}\n\n"
        for r in recs[:5]:  # Top 5
            score = r.get("match_score", 0)
            text += (
                f"- **{r.get('title', 'Unknown')}** by {r.get('provider', 'Unknown')} "
                f"(Match: {score:.0%})\n"
                f"  {r.get('description', '')[:120]}\n"
                f"  [Link]({r.get('url', '#')})\n\n"
            )
        return text
    
    draft_report += format_recommendations("Internship Recommendations", internships)
    draft_report += format_recommendations("Course Recommendations", courses)
    draft_report += format_recommendations("Event Recommendations", events)
    draft_report += format_recommendations("Certification Recommendations", certs)
    
    # Add roadmap
    draft_report += roadmap_text
    
    return {
        "development_roadmap": roadmap_text,
        "draft_report": draft_report,
    }
