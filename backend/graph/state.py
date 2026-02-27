from typing import List, TypedDict, Optional
from enum import Enum

class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Skill(TypedDict):
    name: str
    category: str  # "technical", "soft", "language", "tool"
    level: SkillLevel
    years_experience: Optional[float]

class Experience(TypedDict):
    title: str
    company: str
    duration: str
    description: str
    skills_used: List[str]

class Education(TypedDict):
    degree: str
    field: str
    institution: str
    year: Optional[int]

class Opportunity(TypedDict):
    type: str  # "internship", "course", "event", "certification"
    title: str
    provider: str
    url: str
    description: str
    required_skills: List[str]
    match_score: float
    reason: str

class SkillGap(TypedDict):
    skill: str
    current_level: Optional[SkillLevel]
    target_level: SkillLevel
    priority: str  # "high", "medium", "low"
    recommendation: str

class CareerState(TypedDict):
    # Input
    document_content: str           # Ham döküman içeriği
    document_type: str              # "cv", "resume", "linkedin"
    target_role: Optional[str]      # Hedef pozisyon (opsiyonel)
    
    # Extracted Info
    name: str
    email: Optional[str]
    current_skills: List[Skill]
    experiences: List[Experience]
    education: List[Education]
    
    # Analysis
    skill_gaps: List[SkillGap]
    strengths: List[str]
    areas_to_improve: List[str]
    
    # Recommendations
    internship_recommendations: List[Opportunity]
    course_recommendations: List[Opportunity]
    event_recommendations: List[Opportunity]
    certification_recommendations: List[Opportunity]
    
    # Output
    development_roadmap: str        # 3-6-12 aylık plan
    draft_report: str               # İlk taslak
    critique: str                   # Eleştiri
    final_report: str               # Final rapor
    iteration: int                  # Revizyon sayısı