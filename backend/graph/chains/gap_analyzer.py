"""
Gap Analyzer Chain
Analyzes skill gaps between current skills and target role requirements
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


class SkillGapItem(BaseModel):
    """Model for individual skill gap"""
    skill: str = Field(description="Name of the missing or underdeveloped skill")
    current_level: Optional[str] = Field(default=None, description="Current proficiency level (beginner/intermediate/advanced/expert or None)")
    target_level: str = Field(description="Required proficiency level for the target role")
    priority: str = Field(description="Priority level: 'high', 'medium', or 'low'")
    recommendation: str = Field(description="Specific recommendation to develop this skill")


class GapAnalysisResult(BaseModel):
    """Structured output for gap analysis"""
    skill_gaps: List[SkillGapItem] = Field(description="List of identified skill gaps")
    strengths: List[str] = Field(default=[], description="Current strong skills that match the target role")
    areas_to_improve: List[str] = Field(default=[], description="General areas that need improvement")
    overall_readiness: str = Field(description="Overall assessment of readiness for target role (e.g., 'Ready', 'Needs Development', 'Significant Gap')")
    summary: str = Field(description="Brief summary of the gap analysis")


# Initialize LLM
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# Create the prompt template
GAP_ANALYZER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a career development expert who specializes in skill gap analysis.
Your task is to analyze the gap between a candidate's current skills and the requirements for their target role.
Provide actionable recommendations for each skill gap identified.
Prioritize gaps based on their importance for the target role."""),
    ("human", """Analyze the skill gap for this candidate:

**Current Skills:**
{current_skills}

**Target Role:** {target_role}

**Work Experience:**
{experience_summary}

Please identify:
1. Skills they're missing for the target role
2. Skills they have but need to improve
3. Their current strengths
4. Overall readiness assessment
5. Prioritized recommendations""")
])

# Create the gap analyzer chain with structured output
gap_analyzer_chain = GAP_ANALYZER_PROMPT | llm.with_structured_output(GapAnalysisResult)


def analyze_skill_gaps(
    current_skills: List[str],
    target_role: str,
    experience_summary: str = ""
) -> GapAnalysisResult:
    """
    Analyze skill gaps between current skills and target role requirements.
    
    Args:
        current_skills: List of the candidate's current skills
        target_role: The target job role/position
        experience_summary: Brief summary of work experience
        
    Returns:
        GapAnalysisResult object containing the analysis
    """
    skills_str = ", ".join(current_skills) if current_skills else "No skills provided"
    
    result = gap_analyzer_chain.invoke({
        "current_skills": skills_str,
        "target_role": target_role,
        "experience_summary": experience_summary or "No experience details provided"
    })
    return result