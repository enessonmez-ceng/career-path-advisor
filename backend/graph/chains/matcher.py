"""
Matcher Chain
Scores and ranks opportunities against a user profile using LLM evaluation.
"""
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


class MatchedOpportunity(BaseModel):
    """A single scored opportunity."""
    title: str = Field(description="Opportunity title")
    type: str = Field(description="Type: internship, course, event, certification")
    match_score: float = Field(description="Match score from 0.0 to 1.0", ge=0.0, le=1.0)
    reason: str = Field(description="Why this opportunity is a good match")
    priority_rank: int = Field(description="Priority rank (1 = highest)")


class MatchResult(BaseModel):
    """Structured output for the matching process."""
    matched_opportunities: List[MatchedOpportunity] = Field(
        description="Opportunities ranked by relevance"
    )
    overall_summary: str = Field(
        description="Summary of the matching results and top recommendations"
    )


# Initialize LLM
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# Create the prompt template
MATCHER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a career matching expert who evaluates how well opportunities 
align with a candidate's profile.

Score each opportunity from 0.0 to 1.0 based on:
1. **Skill Match** (40%): Does the candidate have the required skills?
2. **Gap Fill** (30%): Will this opportunity help fill identified skill gaps?
3. **Career Alignment** (20%): Does it move them toward their target role?
4. **Growth Potential** (10%): Does it offer meaningful learning/growth?

Rank all opportunities by score and provide clear reasoning for each."""),
    ("human", """Match and rank these opportunities for the candidate:

**Candidate Profile:**
- Current Skills: {current_skills}
- Target Role: {target_role}
- Skill Gaps: {skill_gaps}
- Strengths: {strengths}

**Opportunities to Evaluate:**
{opportunities}

Rank each opportunity with a match score and explanation.""")
])

# Create the matcher chain
matcher_chain = MATCHER_PROMPT | llm.with_structured_output(MatchResult)


def match_and_rank(
    opportunities: List[dict],
    current_skills: List[str],
    target_role: str,
    skill_gaps: List[str],
    strengths: List[str] = None
) -> MatchResult:
    """
    Match and rank opportunities against a user profile.
    
    Args:
        opportunities: List of opportunity dicts to evaluate
        current_skills: User's current skills
        target_role: Target job role
        skill_gaps: Skills the user needs to develop
        strengths: User's strong skills
        
    Returns:
        MatchResult with ranked and scored opportunities
    """
    # Format opportunities for the prompt
    opp_lines = []
    for i, opp in enumerate(opportunities, 1):
        opp_lines.append(
            f"{i}. [{opp.get('type', 'unknown')}] {opp.get('title', 'Unknown')} "
            f"by {opp.get('provider', 'Unknown')}\n"
            f"   Description: {opp.get('description', 'N/A')[:150]}\n"
            f"   Required Skills: {', '.join(opp.get('required_skills', []))}"
        )
    
    result = matcher_chain.invoke({
        "current_skills": ", ".join(current_skills) if current_skills else "Not specified",
        "target_role": target_role or "Not specified",
        "skill_gaps": ", ".join(skill_gaps) if skill_gaps else "None identified",
        "strengths": ", ".join(strengths) if strengths else "Not specified",
        "opportunities": "\n\n".join(opp_lines) if opp_lines else "No opportunities provided"
    })
    return result
