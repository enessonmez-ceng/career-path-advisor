"""
Opportunity Researcher Chain
Searches for internships, courses, events based on user skills and gaps
Supports: Database lookup, Tavily search, or scraping fallback
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
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
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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
        1. Supabase database (primary — pre-scraped data)
        2. Tavily search (secondary — real-time web search)
        3. LLM suggestions (fill remaining gaps)
    
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
    
    # Build search keywords from skills + role
    search_keywords = list(set(
        (current_skills or []) + (skill_gaps or []) + [target_role]
    ))
    
    # ─── 1. PRIMARY: Query Supabase database ───
    if use_database:
        try:
            from graph.utils.supabase_client import query_opportunities
            
            # Query each category
            db_internships = query_opportunities(
                opp_type="internship", keywords=search_keywords, limit=15
            )
            db_jobs = query_opportunities(
                opp_type="job", keywords=search_keywords, limit=10
            )
            all_opportunities["internships"].extend(db_internships + db_jobs)
            
            db_courses = query_opportunities(
                opp_type="course", keywords=search_keywords, limit=15
            )
            all_opportunities["courses"].extend(db_courses)
            
            db_events = query_opportunities(
                opp_type="event", keywords=search_keywords, limit=10
            )
            all_opportunities["events"].extend(db_events)
            
            db_certs = query_opportunities(
                opp_type="certification", keywords=search_keywords, limit=10
            )
            all_opportunities["certifications"].extend(db_certs)
            
            db_total = sum(len(v) for v in all_opportunities.values())
            print(f"[DB] Found {db_total} opportunities from Supabase")
            
        except Exception as e:
            print(f"[DB] Supabase query error (falling back to Tavily): {e}")
    
    # Check if DB provided enough data
    db_sufficient = all(
        len(all_opportunities[cat]) >= 3
        for cat in ["internships", "courses"]
    )
    
    if db_sufficient:
        print(f"[Fast] Supabase has enough data — skipping Tavily & LLM calls")
    else:
        # ─── 2. SECONDARY: Tavily search (only if DB has few results) ───
        if use_tavily:
            needs_internships = len(all_opportunities["internships"]) < 3
            needs_courses = len(all_opportunities["courses"]) < 3
            needs_events = len(all_opportunities["events"]) < 3
            
            if needs_internships:
                internship_query = f"{target_role} internship {location} 2025"
                tavily_internships = search_with_tavily(internship_query, "internship")
                all_opportunities["internships"].extend(tavily_internships)
            
            if needs_courses and skill_gaps:
                course_query = f"{skill_gaps[0]} online course tutorial"
                tavily_courses = search_with_tavily(course_query, "course")
                all_opportunities["courses"].extend(tavily_courses)
            
            if needs_events:
                event_query = f"tech meetup {location} software developer"
                tavily_events = search_with_tavily(event_query, "event")
                all_opportunities["events"].extend(tavily_events)
        
        # ─── 3. FILL GAPS: LLM suggestions ───
        llm_results = search_opportunities_llm(current_skills, target_role, skill_gaps, location)
        
        # Merge LLM suggestions (convert Pydantic models to dicts)
        all_opportunities["internships"].extend([o.model_dump() for o in llm_results.internships])
        all_opportunities["courses"].extend([o.model_dump() for o in llm_results.courses])
        all_opportunities["events"].extend([o.model_dump() for o in llm_results.events])
        all_opportunities["certifications"].extend([o.model_dump() for o in llm_results.certifications])
        
        # ─── 4. Match and score (only when we have mixed sources) ───
        all_flat = (
            all_opportunities["internships"] + 
            all_opportunities["courses"] + 
            all_opportunities["events"] + 
            all_opportunities["certifications"]
        )
        
        if all_flat:
            try:
                matched = match_opportunities(all_flat, current_skills, target_role, skill_gaps)
                for opp in matched.matched_opportunities:
                    for category in all_opportunities.values():
                        for item in category:
                            if item.get("title") == opp.title:
                                item["match_score"] = opp.match_score
                                item["reason"] = opp.reason or item.get("reason", "")
            except Exception as e:
                print(f"[Matcher] Scoring error: {e}")
    
    # Sort each category by match_score
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
