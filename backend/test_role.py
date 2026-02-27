import sys; sys.path.insert(0, ".")
from graph.graph import career_advisor_graph
import json

dummy_cv = """
Mehmet Yılmaz
mehmet.yilmaz@example.com

SKILLS:
- Solidworks
- AutoCAD
- Thermodynamics
- Fluid Mechanics
- CATIA

EXPERIENCE:
TUSAŞ - Intern (Summer 2024)
- Assisted in aerodynamic design of drone parts using CATIA.
- Performed thermal analysis on engine components.

EDUCATION:
B.Sc. Mechanical Engineering, METU, 2025
"""

state = {
    "document_content": dummy_cv,
    "document_type": "cv",
    "target_role": "", # User didn't type anything
    "name": "",
    "email": None,
    "current_skills": [],
    "experiences": [],
    "education": [],
    "skill_gaps": [],
    "strengths": [],
    "areas_to_improve": [],
    "internship_recommendations": [],
    "course_recommendations": [],
    "event_recommendations": [],
    "certification_recommendations": [],
    "development_roadmap": "",
    "draft_report": "",
    "critique": "",
    "final_report": "",
    "iteration": 0,
}

result = career_advisor_graph.invoke(state)
print("Inferred Target Role:", result.get("target_role"))
print("Current Skills:", [s.get("name") for s in result.get("current_skills", [])])
print("Experiences:", [e.get("company") for e in result.get("experiences", [])])
