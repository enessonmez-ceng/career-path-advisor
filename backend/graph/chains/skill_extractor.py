"""
Skill Extractor Chain
Categorizes and enriches raw skills extracted from CV with detailed information
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from graph.state import SkillLevel


class EnrichedSkill(BaseModel):
    """Detailed skill model with category and proficiency"""
    name: str = Field(description="Skill name")
    category: str = Field(description="Category: 'technical', 'soft', 'language', or 'tool'")
    level: str = Field(description="Proficiency level: 'beginner', 'intermediate', 'advanced', or 'expert'")
    years_experience: Optional[float] = Field(default=None, description="Estimated years of experience with this skill")


class SkillExtractionResult(BaseModel):
    """Structured output for skill extraction"""
    skills: List[EnrichedSkill] = Field(description="List of categorized and enriched skills")
    technical_summary: str = Field(description="Brief summary of technical capabilities")
    soft_skills_summary: str = Field(description="Brief summary of soft skills")


# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create the prompt template
SKILL_EXTRACTOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a career development expert who specializes in skill analysis and categorization.

Your task is to:
1. Categorize each skill into one of: 'technical', 'soft', 'language', 'tool'
2. Estimate the proficiency level based on the work experience provided
3. Estimate years of experience for each skill based on the context

Category definitions:
- technical: Programming languages, frameworks, databases, algorithms, etc.
- soft: Communication, leadership, teamwork, problem-solving, etc.
- language: Human languages (English, Turkish, Spanish, etc.)
- tool: Software tools, IDEs, platforms (Git, Docker, AWS, Figma, etc.)

Level estimation guidelines:
- beginner: Basic understanding, learning phase, <1 year
- intermediate: Can work independently, 1-3 years
- advanced: Deep knowledge, can mentor others, 3-5 years
- expert: Industry-recognized expertise, 5+ years"""),
    ("human", """Analyze and categorize these skills:

**Raw Skills List:**
{skills_list}

**Work Experience Context:**
{experience_context}

Please categorize each skill, estimate proficiency level, and provide summaries.""")
])

# Create the skill extractor chain with structured output
skill_extractor_chain = SKILL_EXTRACTOR_PROMPT | llm.with_structured_output(SkillExtractionResult)


def extract_and_enrich_skills(
    raw_skills: List[str],
    experience_context: str = ""
) -> SkillExtractionResult:
    """
    Take raw skills from CV parser and enrich them with categories and levels.
    
    Args:
        raw_skills: List of skill names extracted from CV
        experience_context: Work experience description to help estimate levels
        
    Returns:
        SkillExtractionResult with categorized and enriched skills
    """
    skills_str = ", ".join(raw_skills) if raw_skills else "No skills provided"
    
    result = skill_extractor_chain.invoke({
        "skills_list": skills_str,
        "experience_context": experience_context or "No experience context provided"
    })
    return result


def convert_to_state_skills(extraction_result: SkillExtractionResult) -> List[dict]:
    """
    Convert SkillExtractionResult to the format expected by CareerState.
    
    Args:
        extraction_result: Result from skill extraction
        
    Returns:
        List of skills in CareerState format
    """
    state_skills = []
    for skill in extraction_result.skills:
        # Map string level to SkillLevel enum
        level_map = {
            "beginner": SkillLevel.BEGINNER,
            "intermediate": SkillLevel.INTERMEDIATE,
            "advanced": SkillLevel.ADVANCED,
            "expert": SkillLevel.EXPERT
        }
        
        state_skills.append({
            "name": skill.name,
            "category": skill.category,
            "level": level_map.get(skill.level.lower(), SkillLevel.BEGINNER),
            "years_experience": skill.years_experience
        })
    
    return state_skills