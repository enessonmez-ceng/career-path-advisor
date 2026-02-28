"""
CV Parser Chain
Extracts structured information from CV/Resume documents
"""
from typing import Dict, Any, List, Optional
from pydantic import Field, BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from graph.utils.document_loader import get_document_content


class Experience(BaseModel):
    """Model for work experience entries"""
    title: str = Field(description="Job title or role")
    company: str = Field(description="Company or organization name")
    duration: str = Field(description="Experience duration (e.g., '2 years', 'Jan 2022 - Present')")
    description: str = Field(description="Brief description of responsibilities and achievements")
    skills_used: List[str] = Field(default=[], description="Skills used in this role")


class Education(BaseModel):
    """Model for education entries"""
    degree: str = Field(description="Degree type (e.g., 'Bachelor's', 'Master's')")
    field: str = Field(description="Field of study")
    institution: str = Field(description="School or university name")
    year: Optional[int] = Field(default=None, description="Graduation year")


class ParsedCV(BaseModel):
    """Structured output model for parsed CV information"""
    name: str = Field(description="Full name of the candidate")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="City/Country location")
    title: Optional[str] = Field(default=None, description="Current or desired job title")
    inferred_target_role: str = Field(description="The most likely target job role/title this person is applying for, inferred from their skills and background (e.g. 'Frontend Developer', 'Mechanical Engineer', 'Data Scientist', 'Automation Engineering Intern')")
    summary: Optional[str] = Field(default=None, description="Professional summary or objective")
    skills: List[str] = Field(default=[], description="List of skills mentioned in the CV")
    experiences: List[Experience] = Field(default=[], description="Work experience entries")
    education: List[Education] = Field(default=[], description="Education entries")
    languages: List[str] = Field(default=[], description="Languages spoken")
    certifications: List[str] = Field(default=[], description="Certifications and courses")


# Initialize LLM
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# Create the prompt template
CV_PARSER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert HR specialist who analyzes CVs and resumes.
Extract all relevant information from the provided CV content and return it in a structured format.
Be thorough and extract as much information as possible. Infer the candidate's target job role based on their profile.
If certain information is not available, leave those fields empty or use default values."""),
    ("human", """Please analyze the following CV content and extract all relevant information:

{cv_content}

Extract the candidate's name, contact info, skills, work experience, education, and infer the most appropriate 'target_role' for them.""")
])

# Create the CV parser chain with structured output
cv_parser_chain = CV_PARSER_PROMPT | llm.with_structured_output(ParsedCV)


def parse_cv(file_path: str) -> ParsedCV:
    """
    Parse a CV file and extract structured information.
    
    Args:
        file_path: Path to the CV file (PDF, DOCX, or TXT)
        
    Returns:
        ParsedCV object containing extracted information
    """
    cv_content = get_document_content(file_path)
    result = cv_parser_chain.invoke({"cv_content": cv_content})
    return result