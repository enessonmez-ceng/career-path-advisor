"""
Electrical Engineering (Elektrik-Elektronik Mühendisliği)
Search queries and static fallback data for scraping.
"""
from typing import List

from scraping.base_scraper import BrightDataClient


# ═══════════════════════════════════════════════════════════
# SEARCH QUERIES
# ═══════════════════════════════════════════════════════════
FIELD_NAME = "Elektrik-Elektronik Mühendisliği"

JOB_QUERIES = [
    "Electrical Engineer",
    "Electrical Engineer Intern",
    "Embedded Systems Engineer",
    "Power Systems Engineer",
    "Control Systems Engineer",
    "Electronics Engineer Intern",
    "RF Engineer",
    "Renewable Energy Engineer",
    "PLC Programmer",
    "IoT Engineer",
]

COURSE_QUERIES = [
    "Electrical circuits",
    "PLC programming",
    "Power electronics",
    "Embedded systems",
    "PCB design",
]


# ═══════════════════════════════════════════════════════════
# STATIC / FALLBACK DATA
# ═══════════════════════════════════════════════════════════
STATIC_DATA = [
    # ── Jobs / Internships ──
    {
        "type": "internship",
        "title": "Elektrik Mühendisi Stajyer",
        "provider": "Siemens Türkiye",
        "url": "https://www.siemens.com.tr/kariyer/elektrik-muhendisi-stajyer-2026",
        "description": "Siemens Türkiye'de elektrik mühendisliği stajı. Enerji dağıtım sistemleri, otomasyon projeleri ve SCADA sistemleri üzerinde çalışma fırsatı.",
        "required_skills": ["AutoCAD", "SCADA", "PLC Programming", "Power Systems", "MATLAB"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-20",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Embedded Systems Engineer Intern",
        "provider": "ASELSAN",
        "url": "https://www.aselsan.com.tr/kariyer/embedded-systems-intern-2026",
        "description": "Embedded Systems Engineering internship at ASELSAN. Work on real-time embedded systems, firmware development in C/C++, and hardware-software integration.",
        "required_skills": ["C", "C++", "Embedded Systems", "RTOS", "ARM", "VHDL"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-18",
        "source": "manual",
    },
    {
        "type": "job",
        "title": "Power Systems Engineer",
        "provider": "ENERJISA",
        "url": "https://www.enerjisa.com.tr/kariyer/power-systems-engineer-2026",
        "description": "Power Systems Engineer at Enerjisa. Design and analyze electrical power distribution networks. ETAP and protection relay coordination experience required.",
        "required_skills": ["Power Systems", "ETAP", "Protection Relays", "MATLAB", "AutoCAD Electrical"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-15",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Control Systems Engineer Intern",
        "provider": "ABB Türkiye",
        "url": "https://www.abb.com/tr/kariyer/control-systems-intern-2026",
        "description": "Control Systems Engineering internship at ABB. Work on industrial automation, PLC/DCS programming, and process control systems.",
        "required_skills": ["PLC", "DCS", "SCADA", "Control Theory", "Siemens TIA Portal"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-22",
        "source": "manual",
    },
    {
        "type": "job",
        "title": "RF/Microwave Engineer",
        "provider": "HAVELSAN",
        "url": "https://www.havelsan.com.tr/kariyer/rf-microwave-engineer-2026",
        "description": "RF/Microwave Engineer at HAVELSAN. Design and test RF circuits, antenna systems, and radar components.",
        "required_skills": ["RF Design", "Antenna Design", "HFSS", "ADS", "PCB Design"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-10",
        "source": "manual",
    },
    {
        "type": "job",
        "title": "Renewable Energy Engineer",
        "provider": "Kalyon Enerji",
        "url": "https://www.kalyonenerji.com.tr/kariyer/renewable-energy-engineer-2026",
        "description": "Renewable Energy Engineer at Kalyon Enerji. Design and optimize solar PV systems, perform energy yield analysis.",
        "required_skills": ["Solar PV", "PVSyst", "Power Electronics", "Grid Integration", "AutoCAD"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-14",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Electronics Design Intern",
        "provider": "Vestel",
        "url": "https://www.vestel.com.tr/kariyer/electronics-design-intern-2026",
        "description": "Electronics Design internship at Vestel. Work on PCB design, circuit simulation with LTspice, and prototype testing.",
        "required_skills": ["PCB Design", "Altium Designer", "LTspice", "Circuit Analysis", "Soldering"],
        "location": "Manisa, Turkey",
        "posted_date": "2026-02-19",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Otomasyon Sistemleri Stajyeri",
        "provider": "BOSCH Sanayi",
        "url": "https://careers.bosch.com/tr/automation-intern-bursa",
        "description": "Endüstri 4.0 dönüşüm projelerinde, PLC programlama ve fabrika otomasyon sistemleri tasarımı üzerine staj.",
        "required_skills": ["PLC", "Automation", "Siemens TIA Portal", "Endüstri 4.0"],
        "location": "Bursa, Turkey",
        "posted_date": "2026-02-25",
        "source": "manual",
    },
    # ── Courses ──
    {
        "type": "course",
        "title": "Circuits and Electronics",
        "provider": "MIT",
        "url": "https://www.edx.org/learn/circuits/mit-circuits-and-electronics",
        "description": "Learn the fundamentals of circuits and electronics from MIT. Linear circuits, op-amps, energy storage elements.",
        "required_skills": ["Circuit Analysis", "Electronics"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    {
        "type": "course",
        "title": "Introduction to Power Electronics",
        "provider": "University of Colorado Boulder",
        "url": "https://www.coursera.org/learn/power-electronics",
        "description": "Learn the basics of power electronics: converters, inverters, and motor drives.",
        "required_skills": ["Power Electronics", "Circuit Analysis", "Control Systems"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    {
        "type": "course",
        "title": "PLC Programming From Scratch",
        "provider": "Paul Lynn",
        "url": "https://www.udemy.com/course/plc-programming-from-scratch/",
        "description": "Learn PLC programming using Siemens TIA Portal. Ladder logic, function blocks, structured text, and HMI design.",
        "required_skills": ["PLC", "Ladder Logic", "Industrial Automation"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "PCB Design with KiCad & Altium",
        "provider": "Robert Feranec",
        "url": "https://www.udemy.com/course/learn-kicad-pcb-design/",
        "description": "Learn professional PCB design from schematic capture to manufacturing. KiCad, Altium Designer, design rules.",
        "required_skills": ["PCB Design", "KiCad", "Altium Designer"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "FPGA Design for Embedded Systems",
        "provider": "University of Colorado Boulder",
        "url": "https://www.coursera.org/specializations/fpga-design",
        "description": "Learn FPGA design using VHDL and Verilog. Digital design fundamentals, synthesis, simulation.",
        "required_skills": ["FPGA", "VHDL", "Verilog", "Digital Design"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    # ── Certifications ──
    {
        "type": "certification",
        "title": "Certified Energy Manager (CEM)",
        "provider": "AEE",
        "url": "https://www.aeecenter.org/certifications/certified-energy-manager",
        "description": "Globally recognized certification for energy managers. Energy auditing, power systems, renewable energy.",
        "required_skills": ["Energy Management", "Power Systems", "Renewable Energy"],
        "location": "Online",
        "posted_date": "",
        "source": "manual",
    },
    {
        "type": "certification",
        "title": "Siemens Certified PLC Programmer",
        "provider": "Siemens",
        "url": "https://www.siemens.com/global/en/products/automation/training/certification.html",
        "description": "Official Siemens certification for PLC programming. TIA Portal, SIMATIC S7 controllers.",
        "required_skills": ["PLC", "Siemens TIA Portal", "Industrial Automation"],
        "location": "Online",
        "posted_date": "",
        "source": "manual",
    },
]


# ═══════════════════════════════════════════════════════════
# SCRAPE FUNCTION
# ═══════════════════════════════════════════════════════════
def scrape(client: BrightDataClient, location: str = "Turkey", max_per_query: int = 10) -> List[dict]:
    """Scrape all Electrical Engineering opportunities."""
    results = list(STATIC_DATA)

    for query in JOB_QUERIES:
        try:
            jobs = client.scrape_linkedin_jobs(query, location, max_per_query)
            results.extend(jobs)
        except Exception as e:
            print(f"  ❌ Error scraping '{query}': {e}")

    return results
