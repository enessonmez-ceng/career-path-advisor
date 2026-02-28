"""
Career Path Advisor - FastAPI Entry Point
Provides REST API endpoints for CV analysis and career recommendations.
"""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables BEFORE importing graph modules
# (chains initialize ChatOpenAI at module level, requiring OPENAI_API_KEY)
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph.graph import career_advisor_graph
from graph.utils.document_loader import SUPPORTED_FORMATS, get_document_content

# Create FastAPI app
app = FastAPI(
    title="Career Path Advisor API",
    description="AI-powered career development assistant that analyzes CVs and provides personalized recommendations.",
    version="1.0.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Career Path Advisor API is running"}


@app.post("/analyze")
async def analyze_cv(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(None),
):
    """
    Analyze a CV file and return career recommendations.
    
    Args:
        file: Uploaded CV file (PDF, DOCX, or TXT)
        target_role: Optional target job role for gap analysis
        
    Returns:
        Complete career analysis with recommendations and roadmap
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported: {SUPPORTED_FORMATS}",
        )
    
    # Save uploaded file to temp location
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract document content
        document_content = get_document_content(temp_path)
        
        if not document_content.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract any content from the uploaded file.",
            )
        
        # Build initial state
        initial_state = {
            "document_content": document_content,
            "document_type": "cv",
            "target_role": target_role or "",
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
        
        # Run the career advisor graph asynchronously
        result = await career_advisor_graph.ainvoke(initial_state)
        
        # Build response (serialize SkillLevel enums to strings)
        def serialize_skills(skills):
            serialized = []
            for s in skills:
                item = dict(s)
                if hasattr(item.get("level"), "value"):
                    item["level"] = item["level"].value
                serialized.append(item)
            return serialized
        
        def serialize_gaps(gaps):
            serialized = []
            for g in gaps:
                item = dict(g)
                if hasattr(item.get("current_level"), "value"):
                    item["current_level"] = item["current_level"].value
                if hasattr(item.get("target_level"), "value"):
                    item["target_level"] = item["target_level"].value
                serialized.append(item)
            return serialized
        
        response = {
            "name": result.get("name", ""),
            "email": result.get("email"),
            "target_role": result.get("target_role", ""),
            "current_skills": serialize_skills(result.get("current_skills", [])),
            "experiences": result.get("experiences", []),
            "education": result.get("education", []),
            "skill_gaps": serialize_gaps(result.get("skill_gaps", [])),
            "strengths": result.get("strengths", []),
            "areas_to_improve": result.get("areas_to_improve", []),
            "internship_recommendations": result.get("internship_recommendations", []),
            "course_recommendations": result.get("course_recommendations", []),
            "event_recommendations": result.get("event_recommendations", []),
            "certification_recommendations": result.get("certification_recommendations", []),
            "development_roadmap": result.get("development_roadmap", ""),
            "final_report": result.get("final_report", ""),
            "critique": result.get("critique", ""),
            "iterations": result.get("iteration", 0),
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing CV: {str(e)}",
        )
    finally:
        # Clean up temp files
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/roles")
async def get_available_roles():
    """Get list of available target roles."""
    from graph.utils.skill_database import get_available_roles
    return {"roles": get_available_roles()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
