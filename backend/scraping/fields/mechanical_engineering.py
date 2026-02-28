"""
Mechanical Engineering (Makine Mühendisliği)
Search queries and static fallback data for scraping.
"""
from typing import List

from scraping.base_scraper import BrightDataClient


# ═══════════════════════════════════════════════════════════
# SEARCH QUERIES
# ═══════════════════════════════════════════════════════════
FIELD_NAME = "Makine Mühendisliği"

JOB_QUERIES = [
    "Mechanical Engineer",
    "Mechanical Engineer Intern",
    "CAD CAM Engineer",
    "HVAC Engineer",
    "Manufacturing Engineer",
    "Structural Analysis Engineer",
    "Automotive R&D Engineer",
    "Robotics Engineer Intern",
    "CFD Simulation Engineer",
    "Production Planning Engineer",
]

COURSE_QUERIES = [
    "SolidWorks CAD",
    "ANSYS FEA",
    "Thermodynamics",
    "Robotics engineering",
    "Lean Six Sigma",
]


# ═══════════════════════════════════════════════════════════
# STATIC / FALLBACK DATA
# ═══════════════════════════════════════════════════════════
STATIC_DATA = [
    # ── Jobs / Internships ──
    {
        "type": "internship",
        "title": "Makine Mühendisi Stajyer",
        "provider": "Ford Otosan",
        "url": "https://www.fordotosan.com.tr/kariyer/makine-muhendisi-stajyer-2026",
        "description": "Ford Otosan'da makine mühendisliği stajı. Otomotiv üretim süreçleri, kalite kontrol, CAD/CAM uygulamaları.",
        "required_skills": ["SolidWorks", "AutoCAD", "GD&T", "Manufacturing", "Quality Control"],
        "location": "Kocaeli, Turkey",
        "posted_date": "2026-02-20",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "HVAC Design Engineer Intern",
        "provider": "Daikin Turkey",
        "url": "https://www.daikin.com.tr/kariyer/hvac-design-intern-2026",
        "description": "HVAC Design Engineering internship at Daikin. Heating, ventilation and air conditioning system design using Revit MEP.",
        "required_skills": ["HVAC", "Revit MEP", "AutoCAD", "Thermodynamics", "Fluid Mechanics"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-18",
        "source": "manual",
    },
    {
        "type": "job",
        "title": "CAD/CAM Engineer",
        "provider": "TUSAŞ (TAI)",
        "url": "https://www.tusas.com/kariyer/cad-cam-engineer-2026",
        "description": "CAD/CAM Engineer at TUSAŞ. Design aerospace components using CATIA V5/V6 and Siemens NX.",
        "required_skills": ["CATIA V5", "Siemens NX", "CNC Programming", "GD&T", "Composites"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-15",
        "source": "manual",
    },
    {
        "type": "job",
        "title": "Structural Analysis Engineer",
        "provider": "ROKETSAN",
        "url": "https://www.roketsan.com.tr/kariyer/structural-analysis-engineer-2026",
        "description": "Structural Analysis Engineer at ROKETSAN. FEA analysis using ANSYS and Abaqus for defense systems.",
        "required_skills": ["ANSYS", "Abaqus", "FEA", "Structural Analysis", "MATLAB"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-10",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Automotive R&D Intern",
        "provider": "TOGG",
        "url": "https://www.togg.com.tr/kariyer/automotive-rd-intern-2026",
        "description": "Automotive R&D internship at TOGG. Electric vehicle powertrain development, battery thermal management.",
        "required_skills": ["SolidWorks", "MATLAB/Simulink", "Thermodynamics", "FEA", "EV Systems"],
        "location": "Bursa, Turkey",
        "posted_date": "2026-02-22",
        "source": "manual",
    },
    {
        "type": "job",
        "title": "Production Planning Engineer",
        "provider": "Arçelik",
        "url": "https://www.arcelik.com.tr/kariyer/production-planning-engineer-2026",
        "description": "Production Planning Engineer at Arçelik. Optimize manufacturing processes using Lean and Six Sigma.",
        "required_skills": ["Lean Manufacturing", "Six Sigma", "SAP", "Production Planning", "Quality Management"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-14",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Robotics Engineer Intern",
        "provider": "FANUC Turkey",
        "url": "https://www.fanuc.com/tr/kariyer/robotics-intern-2026",
        "description": "Robotics Engineering internship at FANUC. Program industrial robots, develop automation cells, robot vision systems.",
        "required_skills": ["Robotics", "PLC", "Robot Programming", "Machine Vision", "ROS"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-19",
        "source": "manual",
    },
    {
        "type": "job",
        "title": "CFD Simulation Engineer",
        "provider": "TEI (TUSAŞ Engine Industries)",
        "url": "https://www.tei.com.tr/kariyer/cfd-simulation-engineer-2026",
        "description": "CFD Simulation Engineer at TEI. Computational fluid dynamics analysis for jet engine components.",
        "required_skills": ["ANSYS Fluent", "CFD", "Fluid Mechanics", "Thermodynamics", "MATLAB"],
        "location": "Eskişehir, Turkey",
        "posted_date": "2026-02-12",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Otomotiv Ar-Ge Stajyeri",
        "provider": "Otokar",
        "url": "https://otokar.com.tr/kariyer/arge-staj-2026",
        "description": "Ticari araç ve savunma sanayi taktik tekerlekli araç tasarımında (CATIA) ve yapısal analiz (Ansys) süreçlerinde staj.",
        "required_skills": ["CATIA", "Ansys", "Automotive Design", "FEA"],
        "location": "Sakarya, Turkey",
        "posted_date": "2026-02-25",
        "source": "manual",
    },
    # ── Courses ──
    {
        "type": "course",
        "title": "Become a SolidWorks Expert",
        "provider": "Paul Shortis",
        "url": "https://www.udemy.com/course/solidworks-zero-to-hero/",
        "description": "Master SolidWorks from scratch. Part modeling, assemblies, drawings, and sheet metal design.",
        "required_skills": ["SolidWorks", "3D Modeling"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "ANSYS FEA for Mechanical Engineers",
        "provider": "Benjamin Sigrist",
        "url": "https://www.udemy.com/course/ansys-fea-mechanical-engineering/",
        "description": "Learn Finite Element Analysis with ANSYS Workbench. Static structural, modal, thermal, and fatigue analysis.",
        "required_skills": ["ANSYS", "FEA", "Structural Analysis"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "Introduction to Thermodynamics",
        "provider": "University of Michigan",
        "url": "https://www.coursera.org/learn/thermodynamics-intro",
        "description": "Learn thermodynamics fundamentals: first and second law, entropy, cycles, and real-world applications.",
        "required_skills": ["Thermodynamics", "Physics", "Mathematics"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    {
        "type": "course",
        "title": "Robotics Specialization",
        "provider": "University of Pennsylvania",
        "url": "https://www.coursera.org/specializations/robotics",
        "description": "Learn robotics fundamentals: kinematics, dynamics, control, perception, and planning.",
        "required_skills": ["Robotics", "MATLAB", "Control Systems"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    {
        "type": "course",
        "title": "Lean Six Sigma Green Belt Certification",
        "provider": "IASSC",
        "url": "https://www.udemy.com/course/lean-six-sigma-green-belt/",
        "description": "Prepare for your Lean Six Sigma Green Belt certification. DMAIC methodology, statistical analysis.",
        "required_skills": ["Six Sigma", "Lean Manufacturing", "Statistics"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    # ── Certifications ──
    {
        "type": "certification",
        "title": "Certified SolidWorks Professional (CSWP)",
        "provider": "Dassault Systèmes",
        "url": "https://www.solidworks.com/certifications/mechanical-design-cswp-702",
        "description": "Industry-recognized certification validating advanced SolidWorks skills.",
        "required_skills": ["SolidWorks", "3D Modeling", "GD&T"],
        "location": "Online",
        "posted_date": "",
        "source": "manual",
    },
    {
        "type": "certification",
        "title": "Six Sigma Black Belt Certification",
        "provider": "ASQ",
        "url": "https://asq.org/cert/six-sigma-black-belt",
        "description": "ASQ Six Sigma Black Belt certification. Process optimization, statistical methods, quality management.",
        "required_skills": ["Six Sigma", "Statistics", "Project Management", "Quality Management"],
        "location": "Online",
        "posted_date": "",
        "source": "manual",
    },
]


# ═══════════════════════════════════════════════════════════
# SCRAPE FUNCTION
# ═══════════════════════════════════════════════════════════
def scrape(client: BrightDataClient, location: str = "Turkey", max_per_query: int = 10) -> List[dict]:
    """Scrape all Mechanical Engineering opportunities."""
    results = list(STATIC_DATA)

    for query in JOB_QUERIES:
        try:
            jobs = client.scrape_linkedin_jobs(query, location, max_per_query)
            results.extend(jobs)
        except Exception as e:
            print(f"  ❌ Error scraping '{query}': {e}")

    return results
