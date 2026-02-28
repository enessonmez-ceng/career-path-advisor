"""
Reviewer Chain
Implements Reflection pattern to critique and improve the draft career report.
Reviews the generated roadmap and recommendations for quality and completeness.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


class CritiqueItem(BaseModel):
    """Individual critique point for the draft report."""
    aspect: str = Field(description="Aspect being critiqued: 'completeness', 'relevance', 'actionability', 'personalization', 'clarity'")
    issue: str = Field(description="Specific issue or weakness identified")
    suggestion: str = Field(description="Concrete suggestion for improvement")
    severity: str = Field(description="Severity level: 'critical', 'major', 'minor'")


class ReviewResult(BaseModel):
    """Structured output for the review process."""
    overall_score: int = Field(description="Overall quality score from 1-10", ge=1, le=10)
    critiques: List[CritiqueItem] = Field(description="List of critique points")
    strengths: List[str] = Field(description="Strong points of the draft report")
    missing_elements: List[str] = Field(description="Important elements that are missing")
    should_revise: bool = Field(description="Whether the report needs revision")
    revision_priority: List[str] = Field(description="Ordered list of aspects to prioritize in revision")
    summary: str = Field(description="Brief summary of the review")


class RevisedReport(BaseModel):
    """Structured output for the revised report."""
    revised_roadmap: str = Field(description="Improved development roadmap")
    revised_recommendations: str = Field(description="Improved recommendations section")
    changes_made: List[str] = Field(description="List of changes made based on critique")
    improvement_notes: str = Field(description="Notes on how the report was improved")


# Initialize LLM
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)


# Critique Prompt - First pass of reflection
CRITIQUE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior career consultant who reviews career development reports.
Your task is to critically evaluate the draft report and identify areas for improvement.

Evaluate based on these criteria:
1. **Completeness**: Does the report cover all necessary aspects (skills, gaps, recommendations)?
2. **Relevance**: Are recommendations aligned with the candidate's goals and current skills?
3. **Actionability**: Are the recommendations specific and actionable?
4. **Personalization**: Is the report tailored to this specific candidate?
5. **Clarity**: Is the report clear, well-organized, and easy to follow?

Be constructive but thorough. Identify both strengths and weaknesses."""),
    ("human", """Review this career development draft report:

**Candidate Profile:**
Name: {candidate_name}
Current Skills: {current_skills}
Target Role: {target_role}

**Identified Skill Gaps:**
{skill_gaps}

**Draft Roadmap:**
{draft_roadmap}

**Draft Recommendations:**
- Internships: {internship_recommendations}
- Courses: {course_recommendations}
- Events: {event_recommendations}

Please provide a comprehensive critique with specific improvement suggestions.""")
])


# Revision Prompt - Second pass to improve the report
REVISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a career development expert who improves career reports based on feedback.
Your task is to revise the draft report addressing all the critiques provided.

Focus on:
1. Addressing all critical and major issues first
2. Making recommendations more specific and actionable
3. Ensuring personalization to the candidate's profile
4. Improving clarity and structure
5. Adding missing elements identified in the review"""),
    ("human", """Revise this career development report based on the critique:

**Original Draft Roadmap:**
{draft_roadmap}

**Original Recommendations:**
{draft_recommendations}

**Critique Summary:**
{critique_summary}

**Specific Issues to Address:**
{issues_to_address}

**Missing Elements:**
{missing_elements}

Please provide a revised, improved version of the report.""")
])


# Create the chains with structured output
critique_chain = CRITIQUE_PROMPT | llm.with_structured_output(ReviewResult)
revision_chain = REVISION_PROMPT | llm.with_structured_output(RevisedReport)


def critique_report(
    candidate_name: str,
    current_skills: List[str],
    target_role: str,
    skill_gaps: List[str],
    draft_roadmap: str,
    internship_recommendations: List[str],
    course_recommendations: List[str],
    event_recommendations: List[str]
) -> ReviewResult:
    """
    Critique the draft career development report.
    
    Args:
        candidate_name: Name of the candidate
        current_skills: List of candidate's current skills
        target_role: Target job role
        skill_gaps: List of identified skill gaps
        draft_roadmap: The draft development roadmap
        internship_recommendations: List of internship recommendations
        course_recommendations: List of course recommendations
        event_recommendations: List of event recommendations
        
    Returns:
        ReviewResult with critique and improvement suggestions
    """
    result = critique_chain.invoke({
        "candidate_name": candidate_name,
        "current_skills": ", ".join(current_skills) if current_skills else "None provided",
        "target_role": target_role or "Not specified",
        "skill_gaps": "\n".join(f"- {gap}" for gap in skill_gaps) if skill_gaps else "None identified",
        "draft_roadmap": draft_roadmap or "No roadmap provided",
        "internship_recommendations": ", ".join(internship_recommendations) if internship_recommendations else "None",
        "course_recommendations": ", ".join(course_recommendations) if course_recommendations else "None",
        "event_recommendations": ", ".join(event_recommendations) if event_recommendations else "None"
    })
    return result


def revise_report(
    draft_roadmap: str,
    draft_recommendations: str,
    review_result: ReviewResult
) -> RevisedReport:
    """
    Revise the draft report based on the critique.
    
    Args:
        draft_roadmap: The original draft roadmap
        draft_recommendations: The original recommendations
        review_result: The critique result from the review
        
    Returns:
        RevisedReport with improved content
    """
    # Extract issues to address
    issues = [f"[{c.severity.upper()}] {c.aspect}: {c.issue}" for c in review_result.critiques]
    
    result = revision_chain.invoke({
        "draft_roadmap": draft_roadmap,
        "draft_recommendations": draft_recommendations,
        "critique_summary": review_result.summary,
        "issues_to_address": "\n".join(issues) if issues else "No major issues",
        "missing_elements": "\n".join(f"- {elem}" for elem in review_result.missing_elements) if review_result.missing_elements else "None"
    })
    return result


def review_and_improve(
    candidate_name: str,
    current_skills: List[str],
    target_role: str,
    skill_gaps: List[str],
    draft_roadmap: str,
    draft_recommendations: str,
    internship_recommendations: List[str],
    course_recommendations: List[str],
    event_recommendations: List[str],
    max_iterations: int = 2
) -> dict:
    """
    Full reflection loop: critique and revise until quality threshold is met.
    
    Args:
        candidate_name: Name of the candidate
        current_skills: List of candidate's current skills  
        target_role: Target job role
        skill_gaps: List of identified skill gaps
        draft_roadmap: Initial draft roadmap
        draft_recommendations: Initial recommendations text
        internship_recommendations: List of internship recommendations
        course_recommendations: List of course recommendations
        event_recommendations: List of event recommendations
        max_iterations: Maximum number of revision iterations
        
    Returns:
        Dictionary containing final report and review history
    """
    current_roadmap = draft_roadmap
    current_recommendations = draft_recommendations
    review_history = []
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Step 1: Critique current draft
        review_result = critique_report(
            candidate_name=candidate_name,
            current_skills=current_skills,
            target_role=target_role,
            skill_gaps=skill_gaps,
            draft_roadmap=current_roadmap,
            internship_recommendations=internship_recommendations,
            course_recommendations=course_recommendations,
            event_recommendations=event_recommendations
        )
        
        review_history.append({
            "iteration": iteration,
            "score": review_result.overall_score,
            "critiques_count": len(review_result.critiques),
            "should_revise": review_result.should_revise
        })
        
        # If quality is sufficient (score >= 8) or no revision needed, stop
        if review_result.overall_score >= 8 or not review_result.should_revise:
            break
            
        # Step 2: Revise based on critique
        revised = revise_report(
            draft_roadmap=current_roadmap,
            draft_recommendations=current_recommendations,
            review_result=review_result
        )
        
        current_roadmap = revised.revised_roadmap
        current_recommendations = revised.revised_recommendations
    
    return {
        "final_roadmap": current_roadmap,
        "final_recommendations": current_recommendations,
        "iterations": iteration,
        "final_score": review_result.overall_score,
        "review_history": review_history,
        "final_strengths": review_result.strengths,
        "remaining_suggestions": [c.suggestion for c in review_result.critiques if c.severity == "minor"]
    }
