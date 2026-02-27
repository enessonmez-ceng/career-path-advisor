from pydantic import BaseModel, Field
from typing import List, Union
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class Course(BaseModel):
    """Represents a course recommendation for learning a skill."""
    target_skill: str = Field(description="The skill to be learned")
    resource: str = Field(description="The source from which the skill can be learned")
    possible_duration: str = Field(description="Estimated completion time of the course based on the individual's experience")


class Project(BaseModel):
    """Represents a project recommendation to apply learned skills."""
    skills_required: List[str] = Field(description="Skills to be used in the project")
    possible_duration: str = Field(description="The time required to complete the project")
    potential_profits: str = Field(description="Benefits that can be gained after the project is completed")


class RoadMap(BaseModel):
    """Represents a complete learning roadmap with courses and projects."""
    hours_per_week: str = Field(description="The number of hours the user will allocate per week for learning")
    steps: List[Union[Course, Project]] = Field(description="Ordered list of learning steps - courses and projects")


ROADMAP_GENERATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a career expert who advises people on which materials they can use to learn their missing skills.
    Your task is:
    1. Determine which courses are best suited to learning the missing skills.
    2. Calculate the potential completion time for these courses.
    3. Suggest a project that the user can undertake immediately after completing a course, allowing them to directly apply and utilise those skills.
    """),
    ("human", """Analyse which courses can be used to learn the missing skills.
    Skills to be learned:
    {skill_list}
    
    Known skills:
    {known_skills}
    """)
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

roadmap_generator_chain = ROADMAP_GENERATOR_PROMPT | llm.with_structured_output(RoadMap)


def create_roadmap(targeted_skills: List[str], known_skills: List[str]) -> RoadMap:
    """Generate a learning roadmap based on targeted and known skills.
    
    Args:
        targeted_skills: List of skills the user wants to learn
        known_skills: List of skills the user already possesses
        
    Returns:
        RoadMap object containing learning steps
    """
    result = roadmap_generator_chain.invoke({
        "skill_list": targeted_skills,
        "known_skills": known_skills
    })
    return result
