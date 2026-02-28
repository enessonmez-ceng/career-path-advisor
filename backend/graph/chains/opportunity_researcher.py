"""
Opportunity Researcher Chain
Searches for internships, courses, events based on user skills and gaps
Supports: Database lookup, Tavily search, or scraping fallback
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch

from graph.state import Opportunity


class OpportunityItem(BaseModel):
    """A single opportunity suggestion from the LLM."""
    type: str = Field(description="Type: internship, course, event, certification")
    title: str = Field(description="Name of the opportunity")
    provider: str = Field(description="Company or platform offering it")
    url: str = Field(description="URL where it can be found")
    description: str = Field(description="Brief description")
    required_skills: List[str] = Field(default=[], description="Skills needed")
    match_score: float = Field(default=0.0, description="Match score 0.0-1.0")
    reason: str = Field(default="", description="Why this is recommended")


class OpportunitySearchResult(BaseModel):
    """Structured output for opportunity search"""
    internships: List[OpportunityItem] = Field(default=[], description="Internship opportunities")
    courses: List[OpportunityItem] = Field(default=[], description="Course recommendations")
    events: List[OpportunityItem] = Field(default=[], description="Events and workshops")
    certifications: List[OpportunityItem] = Field(default=[], description="Certification programs")


class MatchedItem(BaseModel):
    """A single matched and scored opportunity."""
    title: str = Field(description="Title of the opportunity")
    match_score: float = Field(description="Match score 0.0-1.0")
    reason: str = Field(description="Why this opportunity matches")


class OpportunityMatcher(BaseModel):
    """Structured output for matching opportunities to user"""
    matched_opportunities: List[MatchedItem] = Field(description="Opportunities matched to user profile")
    match_reasoning: str = Field(description="Explanation of why these opportunities were selected")


# Initialize LLM
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# Initialize Tavily search
tavily_search = TavilySearch(max_results=5)


# ============ PROMPTS ============

OPPORTUNITY_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a career advisor specializing in finding opportunities for job seekers.
Based on the user's skills, experience, and skill gaps, suggest relevant opportunities.

For each opportunity, provide:
- title: Name of the opportunity
- provider: Company/platform offering it
- url: Where to find it (use realistic URLs)
- description: Brief description
- required_skills: List of skills needed
- match_score: 0.0-1.0 based on fit
- reason: Why this is recommended"""),
    ("human", """Find opportunities for this candidate:

**Current Skills:** {current_skills}
**Target Role:** {target_role}
**Skill Gaps:** {skill_gaps}
**Location:** {location}

Search for:
1. Internships matching their skills
2. Courses to fill skill gaps
3. Relevant events/workshops
4. Useful certifications""")
])

OPPORTUNITY_MATCHER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at matching job opportunities to candidates.
Analyze the provided opportunities and rank them based on:
1. Skill match (do they have the required skills?)
2. Growth potential (will it help fill their gaps?)
3. Relevance to target role
4. Location compatibility

For each opportunity, assign a match_score (0.0-1.0) and explain why."""),
    ("human", """Match these opportunities to the candidate:

**Candidate Skills:** {current_skills}
**Target Role:** {target_role}
**Skill Gaps:** {skill_gaps}

**Available Opportunities:**
{opportunities}

Rank and score each opportunity.""")
])


# ============ CHAINS ============

opportunity_search_chain = OPPORTUNITY_SEARCH_PROMPT | llm.with_structured_output(OpportunitySearchResult)
opportunity_matcher_chain = OPPORTUNITY_MATCHER_PROMPT | llm.with_structured_output(OpportunityMatcher)


# ============ FUNCTIONS ============

def search_with_tavily(query: str, search_type: str = "internship") -> List[dict]:
    """
    Search for opportunities using Tavily API.
    
    Args:
        query: Search query (e.g., "Python developer internship Istanbul")
        search_type: Type of opportunity (internship, course, event, certification)
        
    Returns:
        List of opportunities in Opportunity format
    """
    try:
        results = tavily_search.invoke({"query": query})
        
        opportunities = []
        for result in results:
            opportunities.append({
                "type": search_type,
                "title": result.get("title", ""),
                "provider": result.get("source", "Unknown"),
                "url": result.get("url", ""),
                "description": result.get("content", "")[:200],
                "required_skills": [],
                "match_score": 0.0,
                "reason": "Found via web search"
            })
        return opportunities
    except Exception as e:
        print(f"Tavily search error: {e}")
        return []


def search_opportunities_llm(
    current_skills: List[str],
    target_role: str,
    skill_gaps: List[str],
    location: str = "Turkey"
) -> OpportunitySearchResult:
    """
    Use LLM to suggest opportunities based on profile.
    
    Args:
        current_skills: User's current skills
        target_role: Target job role
        skill_gaps: Skills the user needs to develop
        location: Preferred location
        
    Returns:
        OpportunitySearchResult with categorized opportunities
    """
    result = opportunity_search_chain.invoke({
        "current_skills": ", ".join(current_skills) if current_skills else "Not specified",
        "target_role": target_role or "Not specified",
        "skill_gaps": ", ".join(skill_gaps) if skill_gaps else "None identified",
        "location": location
    })
    return result


def match_opportunities(
    opportunities: List[dict],
    current_skills: List[str],
    target_role: str,
    skill_gaps: List[str]
) -> OpportunityMatcher:
    """
    Match and rank opportunities for a specific user.
    
    Args:
        opportunities: List of available opportunities
        current_skills: User's current skills
        target_role: Target job role
        skill_gaps: Skills to develop
        
    Returns:
        OpportunityMatcher with ranked opportunities
    """
    # Format opportunities for prompt
    opp_text = "\n".join([
        f"- {opp.get('title', 'Unknown')} at {opp.get('provider', 'Unknown')}: {opp.get('description', '')[:100]}"
        for opp in opportunities
    ])
    
    result = opportunity_matcher_chain.invoke({
        "current_skills": ", ".join(current_skills) if current_skills else "Not specified",
        "target_role": target_role or "Not specified",
        "skill_gaps": ", ".join(skill_gaps) if skill_gaps else "None identified",
        "opportunities": opp_text
    })
    return result


def research_opportunities(
    current_skills: List[str],
    target_role: str,
    skill_gaps: List[str],
    location: str = "Turkey",
    use_tavily: bool = True,
    use_database: bool = True,
) -> dict:
    """
    Main function to research all types of opportunities.
    
    Priority:
        1. Semantic search via pgvector (primary — embedding similarity)
        2. Keyword DB fallback (if semantic search fails/empty)
        3. Tavily search (secondary — real-time web search)
        4. LLM suggestions (fill remaining gaps)
    
    Args:
        current_skills: User's current skills
        target_role: Target job role
        skill_gaps: Skills to develop
        location: Preferred location
        use_tavily: Whether to use Tavily for real-time search
        use_database: Whether to query Supabase database
        
    Returns:
        Dict with categorized opportunities
    """
    all_opportunities = {
        "internships": [],
        "courses": [],
        "events": [],
        "certifications": []
    }
    
    # ─── 1. PRIMARY: Semantic Search via pgvector ───
    if use_database:
        try:
            from graph.utils.embedding_service import generate_profile_embedding
            from graph.utils.supabase_client import semantic_search, query_opportunities
            
            # Build user profile embedding
            education_field = ""  # Could be extracted from state if available
            profile_embedding = generate_profile_embedding(
                skills=current_skills or [],
                target_role=target_role,
                education_field=education_field,
                skill_gaps=skill_gaps or [],
            )
            
            if profile_embedding:
                # Semantic search for each category
                all_db_results = semantic_search(
                    query_embedding=profile_embedding,
                    match_count=50,
                    match_threshold=0.25,
                )
                
                # Categorize results
                for opp in all_db_results:
                    opp_type = opp.get("type", "job")
                    if opp_type in ("internship", "job"):
                        all_opportunities["internships"].append(opp)
                    elif opp_type == "course":
                        all_opportunities["courses"].append(opp)
                    elif opp_type == "event":
                        all_opportunities["events"].append(opp)
                    elif opp_type == "certification":
                        all_opportunities["certifications"].append(opp)
                
                db_total = sum(len(v) for v in all_opportunities.values())
                print(f"[Semantic] Found {db_total} opportunities via pgvector")
            else:
                print("[Semantic] Could not generate profile embedding, falling back to keyword search")
                # Fallback to keyword search
                search_keywords = list(set(
                    (current_skills or []) + (skill_gaps or []) + [target_role]
                ))
                db_internships = query_opportunities(opp_type="internship", keywords=search_keywords, limit=15)
                db_jobs = query_opportunities(opp_type="job", keywords=search_keywords, limit=10)
                all_opportunities["internships"].extend(db_internships + db_jobs)
                db_courses = query_opportunities(opp_type="course", keywords=search_keywords, limit=15)
                all_opportunities["courses"].extend(db_courses)
                
        except Exception as e:
            print(f"[Semantic] Search error (falling back to Tavily): {e}")
    
    # Check if DB provided enough data
    db_sufficient = all(
        len(all_opportunities[cat]) >= 3
        for cat in ["internships", "courses"]
    )
    
    if db_sufficient:
        print(f"[Fast] Semantic search has enough data — skipping LLM & Tavily")
    elif use_tavily:
        print("[Fast] Not enough data in DB, but LLM & Tavily are disabled for performance.")
        
    # Sıralama (Eğer skill matcher henüz çalışmadıysa basitçe döndür)
    for category in all_opportunities:
        all_opportunities[category] = sorted(
            all_opportunities[category],
            key=lambda x: x.get("match_score", 0),
            reverse=True
        )
    
    all_flat = sum(len(v) for k, v in all_opportunities.items() if k != "total_found")
    all_opportunities["total_found"] = all_flat
    
    return all_opportunities


# ============ CONVENIENCE FUNCTIONS ============

def get_top_internships(
    skills: List[str],
    target_role: str,
    location: str = "Turkey",
    limit: int = 5
) -> List[dict]:
    """Get top matched internships"""
    results = research_opportunities(skills, target_role, [], location)
    return results["internships"][:limit]


def get_top_courses(
    skill_gaps: List[str],
    limit: int = 5
) -> List[dict]:
    """Get top courses for skill gaps"""
    results = research_opportunities([], "", skill_gaps)
    return results["courses"][:limit]
