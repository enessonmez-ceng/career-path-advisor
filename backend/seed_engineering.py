"""
Seed Engineering Departments
Populates the Supabase database with opportunities for:
  - Bilgisayar Mühendisliği (Computer Engineering)
  - Elektrik Mühendisliği (Electrical Engineering)
  - Makine Mühendisliği (Mechanical Engineering)

Usage:
    python seed_engineering.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from graph.utils.supabase_client import upsert_opportunities, get_stats

# ──────────────────────────────────────────────
# Try importing scrapers (may fail on some envs)
# ──────────────────────────────────────────────
try:
    from graph.utils.job_scraper import scrape_linkedin_jobs
    from graph.utils.course_scraper import scrape_udemy, scrape_coursera
    from graph.utils.indeed_scraper import scrape_indeed
    SCRAPERS_AVAILABLE = True
except ImportError:
    SCRAPERS_AVAILABLE = False
    print("⚠️  Scrapers not available, using static data only.")


# ═══════════════════════════════════════════════
# STATIC / FALLBACK DATA
# ═══════════════════════════════════════════════

COMPUTER_ENGINEERING_DATA = [
    # ---- Jobs / Internships ----
    {
        "type": "internship",
        "title": "Software Engineering Intern",
        "provider": "Google",
        "url": "https://careers.google.com/jobs/software-engineering-intern-2026",
        "description": "Join Google as a Software Engineering Intern. Work on large-scale distributed systems, develop production code in Python/Java/C++, and collaborate with world-class engineers.",
        "required_skills": ["Python", "Java", "C++", "Data Structures", "Algorithms"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-20",
        "source": "linkedin",
    },
    {
        "type": "internship",
        "title": "Backend Developer Intern",
        "provider": "Trendyol",
        "url": "https://www.trendyol.com/careers/backend-developer-intern-2026",
        "description": "Backend Developer Intern position at Trendyol. Develop RESTful APIs using Java/Spring Boot, work with microservices architecture and Kubernetes.",
        "required_skills": ["Java", "Spring Boot", "REST API", "Microservices", "Docker"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-18",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "Full Stack Developer",
        "provider": "Getir",
        "url": "https://getir.com/careers/full-stack-developer-2026",
        "description": "Full Stack Developer role at Getir. Build and maintain web applications using React and Node.js. Experience with PostgreSQL and Redis required.",
        "required_skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "Redis"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-15",
        "source": "linkedin",
    },
    {
        "type": "internship",
        "title": "Data Science Intern",
        "provider": "Turkcell",
        "url": "https://www.turkcell.com.tr/kariyer/data-science-intern-2026",
        "description": "Data Science internship at Turkcell. Work on machine learning models for customer analytics, NLP projects, and big data pipelines using Python and Spark.",
        "required_skills": ["Python", "Machine Learning", "Pandas", "TensorFlow", "SQL"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-22",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "DevOps Engineer",
        "provider": "Hepsiburada",
        "url": "https://www.hepsiburada.com/careers/devops-engineer-2026",
        "description": "DevOps Engineer at Hepsiburada. Manage CI/CD pipelines, Kubernetes clusters, and cloud infrastructure on AWS. Automate deployment processes.",
        "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Linux"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-10",
        "source": "indeed",
    },
    {
        "type": "internship",
        "title": "Mobile App Developer Intern",
        "provider": "Insider",
        "url": "https://useinsider.com/careers/mobile-developer-intern-2026",
        "description": "Mobile App Developer Intern at Insider. Develop cross-platform mobile applications using Flutter/Dart. Work on push notification systems and analytics SDKs.",
        "required_skills": ["Flutter", "Dart", "Mobile Development", "REST API", "Git"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-19",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "Cybersecurity Analyst",
        "provider": "STM Savunma",
        "url": "https://www.stm.com.tr/kariyer/cybersecurity-analyst-2026",
        "description": "Cybersecurity Analyst at STM. Conduct penetration testing, vulnerability assessments, and incident response for defense systems. SIEM and network security experience required.",
        "required_skills": ["Network Security", "Penetration Testing", "SIEM", "Linux", "Python"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-12",
        "source": "indeed",
    },
    {
        "type": "job",
        "title": "AI/ML Engineer",
        "provider": "Peak Games",
        "url": "https://www.peakgames.com/careers/ai-ml-engineer-2026",
        "description": "AI/ML Engineer at Peak Games. Build recommendation engines and predictive models for gaming analytics. Deep learning experience with PyTorch preferred.",
        "required_skills": ["Python", "PyTorch", "Deep Learning", "MLOps", "SQL", "Statistics"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-14",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "Cloud Solutions Architect",
        "provider": "Microsoft Turkey",
        "url": "https://careers.microsoft.com/cloud-architect-turkey-2026",
        "description": "Cloud Solutions Architect at Microsoft Turkey. Design and implement cloud-native solutions on Azure. Help enterprise customers with digital transformation.",
        "required_skills": ["Azure", "Cloud Architecture", "Microservices", "DevOps", "Python"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-08",
        "source": "linkedin",
    },
    {
        "type": "internship",
        "title": "Frontend Developer Intern",
        "provider": "Yemeksepeti",
        "url": "https://www.yemeksepeti.com/kariyer/frontend-intern-2026",
        "description": "Frontend Developer Intern at Yemeksepeti. Build responsive web interfaces using React/Next.js. Strong CSS and UI/UX skills required.",
        "required_skills": ["React", "Next.js", "JavaScript", "CSS", "HTML", "Figma"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-21",
        "source": "linkedin",
    },
    # ---- Courses ----
    {
        "type": "course",
        "title": "The Complete Python Bootcamp From Zero to Hero",
        "provider": "Jose Portilla",
        "url": "https://www.udemy.com/course/complete-python-bootcamp/",
        "description": "Learn Python like a Professional: start from basics and go all the way to creating your own applications and games. Includes OOP, decorators, generators.",
        "required_skills": ["Python"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "Machine Learning Specialization",
        "provider": "Stanford University",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "description": "Andrew Ng's Machine Learning course. Learn supervised/unsupervised learning, neural networks, and practical ML techniques using Python and TensorFlow.",
        "required_skills": ["Python", "Machine Learning", "Linear Algebra"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    {
        "type": "course",
        "title": "Full-Stack Web Development with React",
        "provider": "Hong Kong University",
        "url": "https://www.coursera.org/specializations/full-stack-react",
        "description": "Master front-end web development with React, server-side with Node.js and Express, and databases with MongoDB. Build full-stack applications.",
        "required_skills": ["React", "Node.js", "MongoDB", "JavaScript"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    {
        "type": "course",
        "title": "Docker & Kubernetes: The Practical Guide",
        "provider": "Academind",
        "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/",
        "description": "Learn Docker, Docker Compose, Multi-Container Projects, Deployment, and Kubernetes from scratch. Hands-on demonstrations and real projects.",
        "required_skills": ["Docker", "Kubernetes", "DevOps"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "CS50: Introduction to Computer Science",
        "provider": "Harvard University",
        "url": "https://www.edx.org/learn/computer-science/harvard-university-cs50",
        "description": "Harvard's introduction to computer science. Topics include abstraction, algorithms, data structures, encapsulation, resource management, security, and web development.",
        "required_skills": ["C", "Python", "SQL", "Algorithms"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    {
        "type": "course",
        "title": "AWS Certified Solutions Architect Associate",
        "provider": "Stephane Maarek",
        "url": "https://www.udemy.com/course/aws-certified-solutions-architect-associate/",
        "description": "Pass the AWS Solutions Architect Associate exam. Learn EC2, S3, RDS, VPC, Lambda, and more. Hands-on labs and practice exams included.",
        "required_skills": ["AWS", "Cloud Computing", "Networking"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    # ---- Certifications ----
    {
        "type": "certification",
        "title": "Google Cloud Professional Cloud Architect",
        "provider": "Google Cloud",
        "url": "https://cloud.google.com/certification/cloud-architect",
        "description": "Validate your ability to design, develop, and manage robust, secure cloud architectures on Google Cloud Platform.",
        "required_skills": ["GCP", "Cloud Architecture", "Networking", "Security"],
        "location": "Online",
        "posted_date": "",
        "source": "manual",
    },
    {
        "type": "certification",
        "title": "Meta Front-End Developer Professional Certificate",
        "provider": "Meta",
        "url": "https://www.coursera.org/professional-certificates/meta-front-end-developer",
        "description": "Get started in front-end development. Learn HTML, CSS, JavaScript, React and prepare for a career as a front-end developer.",
        "required_skills": ["React", "JavaScript", "HTML", "CSS"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
]

ELECTRICAL_ENGINEERING_DATA = [
    # ---- Jobs / Internships ----
    {
        "type": "internship",
        "title": "Elektrik Mühendisi Stajyer",
        "provider": "Siemens Türkiye",
        "url": "https://www.siemens.com.tr/kariyer/elektrik-muhendisi-stajyer-2026",
        "description": "Siemens Türkiye'de elektrik mühendisliği stajı. Enerji dağıtım sistemleri, otomasyon projeleri ve SCADA sistemleri üzerinde çalışma fırsatı.",
        "required_skills": ["AutoCAD", "SCADA", "PLC Programming", "Power Systems", "MATLAB"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-20",
        "source": "linkedin",
    },
    {
        "type": "internship",
        "title": "Embedded Systems Engineer Intern",
        "provider": "ASELSAN",
        "url": "https://www.aselsan.com.tr/kariyer/embedded-systems-intern-2026",
        "description": "Embedded Systems Engineering internship at ASELSAN. Work on real-time embedded systems, firmware development in C/C++, and hardware-software integration for defense systems.",
        "required_skills": ["C", "C++", "Embedded Systems", "RTOS", "ARM", "VHDL"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-18",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "Power Systems Engineer",
        "provider": "ENERJISA",
        "url": "https://www.enerjisa.com.tr/kariyer/power-systems-engineer-2026",
        "description": "Power Systems Engineer at Enerjisa. Design and analyze electrical power distribution networks. Experience with ETAP, PSS/E, and protection relay coordination required.",
        "required_skills": ["Power Systems", "ETAP", "Protection Relays", "MATLAB", "AutoCAD Electrical"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-15",
        "source": "indeed",
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
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "RF/Microwave Engineer",
        "provider": "HAVELSAN",
        "url": "https://www.havelsan.com.tr/kariyer/rf-microwave-engineer-2026",
        "description": "RF/Microwave Engineer at HAVELSAN. Design and test RF circuits, antenna systems, and radar components. Experience with ADS, HFSS, and CST required.",
        "required_skills": ["RF Design", "Antenna Design", "HFSS", "ADS", "PCB Design"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-10",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "Renewable Energy Engineer",
        "provider": "Kalyon Enerji",
        "url": "https://www.kalyonenerji.com.tr/kariyer/renewable-energy-engineer-2026",
        "description": "Renewable Energy Engineer at Kalyon Enerji. Design and optimize solar PV systems, perform energy yield analysis, and manage grid integration. PVSyst experience required.",
        "required_skills": ["Solar PV", "PVSyst", "Power Electronics", "Grid Integration", "AutoCAD"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-14",
        "source": "indeed",
    },
    {
        "type": "internship",
        "title": "Electronics Design Intern",
        "provider": "Vestel",
        "url": "https://www.vestel.com.tr/kariyer/electronics-design-intern-2026",
        "description": "Electronics Design internship at Vestel. Work on PCB design, circuit simulation with LTspice, and prototype testing for consumer electronics products.",
        "required_skills": ["PCB Design", "Altium Designer", "LTspice", "Circuit Analysis", "Soldering"],
        "location": "Manisa, Turkey",
        "posted_date": "2026-02-19",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "Electrical Project Engineer",
        "provider": "Schneider Electric Turkey",
        "url": "https://www.se.com/tr/kariyer/electrical-project-engineer-2026",
        "description": "Electrical Project Engineer at Schneider Electric. Manage electrical installation projects, design MV/LV distribution systems, and coordinate with contractors.",
        "required_skills": ["Electrical Design", "AutoCAD Electrical", "EPLAN", "MV/LV Systems", "Project Management"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-12",
        "source": "indeed",
    },
    {
        "type": "job",
        "title": "IoT Solutions Engineer",
        "provider": "Arçelik",
        "url": "https://www.arcelik.com.tr/kariyer/iot-solutions-engineer-2026",
        "description": "IoT Solutions Engineer at Arçelik. Develop IoT platforms for smart home devices, work with MQTT, BLE, and WiFi protocols. Firmware and cloud integration.",
        "required_skills": ["IoT", "MQTT", "Embedded C", "BLE", "WiFi", "AWS IoT"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-08",
        "source": "linkedin",
    },
    {
        "type": "internship",
        "title": "Signal Processing Intern",
        "provider": "TUSAŞ (TAI)",
        "url": "https://www.tusas.com/kariyer/signal-processing-intern-2026",
        "description": "Signal Processing internship at TUSAŞ. Work on digital signal processing algorithms, radar signal analysis, and FPGA implementation using MATLAB and VHDL.",
        "required_skills": ["MATLAB", "Signal Processing", "FPGA", "VHDL", "DSP"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-21",
        "source": "linkedin",
    },
    # ---- Courses ----
    {
        "type": "course",
        "title": "Circuits and Electronics",
        "provider": "MIT",
        "url": "https://www.edx.org/learn/circuits/mit-circuits-and-electronics",
        "description": "Learn the fundamentals of circuits and electronics from MIT. Topics include linear circuits, op-amps, energy storage elements, and first/second-order circuits.",
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
        "description": "Learn the basics of power electronics: converters, inverters, and motor drives. Understand DC-DC, AC-DC, and DC-AC conversion techniques.",
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
        "description": "Learn PLC programming using Siemens TIA Portal. Cover ladder logic, function blocks, structured text, and HMI design for industrial automation.",
        "required_skills": ["PLC", "Ladder Logic", "Industrial Automation"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "MATLAB Onramp & Signal Processing",
        "provider": "MathWorks",
        "url": "https://www.mathworks.com/learn/tutorials/matlab-onramp.html",
        "description": "Free interactive MATLAB tutorial covering fundamentals, signal processing, and data analysis. Perfect for electrical engineering students.",
        "required_skills": ["MATLAB", "Signal Processing"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "PCB Design with KiCad & Altium",
        "provider": "Robert Feranec",
        "url": "https://www.udemy.com/course/learn-kicad-pcb-design/",
        "description": "Learn professional PCB design from schematic capture to manufacturing. Covers KiCad, Altium Designer, design rules, and signal integrity.",
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
        "description": "Learn FPGA design using VHDL and Verilog. Cover digital design fundamentals, synthesis, simulation, and implement real-world embedded system projects.",
        "required_skills": ["FPGA", "VHDL", "Verilog", "Digital Design"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    # ---- Certifications ----
    {
        "type": "certification",
        "title": "Certified Energy Manager (CEM)",
        "provider": "AEE",
        "url": "https://www.aeecenter.org/certifications/certified-energy-manager",
        "description": "Globally recognized certification for energy managers. Covers energy auditing, power systems, renewable energy, and energy management best practices.",
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
        "description": "Official Siemens certification for PLC programming. Validates expertise in TIA Portal, SIMATIC S7 controllers, and industrial network configuration.",
        "required_skills": ["PLC", "Siemens TIA Portal", "Industrial Automation"],
        "location": "Online",
        "posted_date": "",
        "source": "manual",
    },
]

MECHANICAL_ENGINEERING_DATA = [
    # ---- Jobs / Internships ----
    {
        "type": "internship",
        "title": "Makine Mühendisi Stajyer",
        "provider": "Ford Otosan",
        "url": "https://www.fordotosan.com.tr/kariyer/makine-muhendisi-stajyer-2026",
        "description": "Ford Otosan'da makine mühendisliği stajı. Otomotiv üretim süreçleri, kalite kontrol, CAD/CAM uygulamaları ve APQP süreçleri üzerinde çalışma.",
        "required_skills": ["SolidWorks", "AutoCAD", "GD&T", "Manufacturing", "Quality Control"],
        "location": "Kocaeli, Turkey",
        "posted_date": "2026-02-20",
        "source": "linkedin",
    },
    {
        "type": "internship",
        "title": "HVAC Design Engineer Intern",
        "provider": "Daikin Turkey",
        "url": "https://www.daikin.com.tr/kariyer/hvac-design-intern-2026",
        "description": "HVAC Design Engineering internship at Daikin. Work on heating, ventilation and air conditioning system design using Revit MEP and HAP software.",
        "required_skills": ["HVAC", "Revit MEP", "AutoCAD", "Thermodynamics", "Fluid Mechanics"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-18",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "CAD/CAM Engineer",
        "provider": "TUSAŞ (TAI)",
        "url": "https://www.tusas.com/kariyer/cad-cam-engineer-2026",
        "description": "CAD/CAM Engineer at TUSAŞ. Design aerospace components using CATIA V5/V6 and Siemens NX. CNC programming and composite material experience preferred.",
        "required_skills": ["CATIA V5", "Siemens NX", "CNC Programming", "GD&T", "Composites"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-15",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "Structural Analysis Engineer",
        "provider": "ROKETSAN",
        "url": "https://www.roketsan.com.tr/kariyer/structural-analysis-engineer-2026",
        "description": "Structural Analysis Engineer at ROKETSAN. Perform FEA analysis using ANSYS and Abaqus. Design and validate structural components for defense systems.",
        "required_skills": ["ANSYS", "Abaqus", "FEA", "Structural Analysis", "MATLAB"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-10",
        "source": "indeed",
    },
    {
        "type": "internship",
        "title": "Automotive R&D Intern",
        "provider": "TOGG",
        "url": "https://www.togg.com.tr/kariyer/automotive-rd-intern-2026",
        "description": "Automotive R&D internship at TOGG. Work on electric vehicle powertrain development, battery thermal management, and vehicle dynamics simulations.",
        "required_skills": ["SolidWorks", "MATLAB/Simulink", "Thermodynamics", "FEA", "EV Systems"],
        "location": "Bursa, Turkey",
        "posted_date": "2026-02-22",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "Production Planning Engineer",
        "provider": "Arçelik",
        "url": "https://www.arcelik.com.tr/kariyer/production-planning-engineer-2026",
        "description": "Production Planning Engineer at Arçelik. Optimize manufacturing processes using Lean and Six Sigma methodologies. Manage production schedules and quality systems.",
        "required_skills": ["Lean Manufacturing", "Six Sigma", "SAP", "Production Planning", "Quality Management"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-14",
        "source": "indeed",
    },
    {
        "type": "internship",
        "title": "Robotics Engineer Intern",
        "provider": "FANUC Turkey",
        "url": "https://www.fanuc.com/tr/kariyer/robotics-intern-2026",
        "description": "Robotics Engineering internship at FANUC. Program industrial robots, develop automation cells, and work on robot vision systems integration.",
        "required_skills": ["Robotics", "PLC", "Robot Programming", "Machine Vision", "ROS"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-19",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "CFD Simulation Engineer",
        "provider": "TEI (TUSAŞ Engine Industries)",
        "url": "https://www.tei.com.tr/kariyer/cfd-simulation-engineer-2026",
        "description": "CFD Simulation Engineer at TEI. Perform computational fluid dynamics analysis for jet engine components using ANSYS Fluent and CFX.",
        "required_skills": ["ANSYS Fluent", "CFD", "Fluid Mechanics", "Thermodynamics", "MATLAB"],
        "location": "Eskişehir, Turkey",
        "posted_date": "2026-02-12",
        "source": "linkedin",
    },
    {
        "type": "job",
        "title": "3D Printing / Additive Manufacturing Engineer",
        "provider": "BAYKAR",
        "url": "https://www.baykartech.com/kariyer/additive-manufacturing-engineer-2026",
        "description": "Additive Manufacturing Engineer at BAYKAR. Develop 3D printing processes for aerospace-grade metal parts. Design for AM using topology optimization.",
        "required_skills": ["3D Printing", "Metal AM", "Topology Optimization", "SolidWorks", "Materials Science"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-08",
        "source": "indeed",
    },
    {
        "type": "internship",
        "title": "Maintenance Engineer Intern",
        "provider": "Turkish Airlines (THY Teknik)",
        "url": "https://www.thyao.com/kariyer/maintenance-engineer-intern-2026",
        "description": "Maintenance Engineering internship at THY Teknik. Work on aircraft maintenance, NDT inspections, and engine overhaul processes.",
        "required_skills": ["Aircraft Maintenance", "NDT", "Quality Control", "Technical Writing", "Safety"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-21",
        "source": "linkedin",
    },
    # ---- Courses ----
    {
        "type": "course",
        "title": "Become a SolidWorks Expert",
        "provider": "Paul Shortis",
        "url": "https://www.udemy.com/course/solidworks-zero-to-hero/",
        "description": "Master SolidWorks from scratch. Learn part modeling, assemblies, drawings, and sheet metal design. Complete hands-on projects included.",
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
        "description": "Learn Finite Element Analysis with ANSYS Workbench. Cover static structural, modal, thermal, and fatigue analysis with real engineering examples.",
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
        "description": "Learn thermodynamics fundamentals: first and second law, entropy, cycles, and real-world applications in engines and power plants.",
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
        "description": "Learn robotics fundamentals: kinematics, dynamics, control, perception, and planning. Build and program robots in simulation.",
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
        "description": "Prepare for your Lean Six Sigma Green Belt certification. Learn DMAIC methodology, statistical analysis, and process improvement techniques.",
        "required_skills": ["Six Sigma", "Lean Manufacturing", "Statistics"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    {
        "type": "course",
        "title": "MATLAB for Mechanical Engineers",
        "provider": "Ilyas Kandemir",
        "url": "https://www.udemy.com/course/matlab-for-mechanical-engineers/",
        "description": "Learn MATLAB programming specifically for mechanical engineering applications: stress analysis, vibration simulation, and thermal modeling.",
        "required_skills": ["MATLAB", "Numerical Methods"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    # ---- Certifications ----
    {
        "type": "certification",
        "title": "Certified SolidWorks Professional (CSWP)",
        "provider": "Dassault Systèmes",
        "url": "https://www.solidworks.com/certifications/mechanical-design-cswp-702",
        "description": "Industry-recognized certification validating advanced SolidWorks skills in part modeling, assemblies, and drawing creation.",
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
        "description": "ASQ Six Sigma Black Belt certification. Demonstrate expertise in process optimization, statistical methods, and quality management systems.",
        "required_skills": ["Six Sigma", "Statistics", "Project Management", "Quality Management"],
        "location": "Online",
        "posted_date": "",
        "source": "manual",
    },
]


# ═══════════════════════════════════════════════
# SCRAPING TARGETS per department
# ═══════════════════════════════════════════════
SCRAPE_TARGETS = {
    "Bilgisayar Mühendisliği": [
        "Software Engineer",
        "Backend Developer",
        "Data Scientist",
        "Full Stack Developer",
        "DevOps Engineer",
    ],
    "Elektrik Mühendisliği": [
        "Electrical Engineer",
        "Embedded Systems Engineer",
        "Power Systems Engineer",
        "Control Systems Engineer",
        "Electronics Engineer",
    ],
    "Makine Mühendisliği": [
        "Mechanical Engineer",
        "CAD CAM Engineer",
        "HVAC Engineer",
        "Manufacturing Engineer",
        "Structural Engineer",
    ],
}


def seed_static_data():
    """Insert all static/curated data into Supabase."""
    print("\n" + "=" * 60)
    print("📦  Seeding STATIC data into Supabase...")
    print("=" * 60)

    datasets = {
        "Bilgisayar Mühendisliği": COMPUTER_ENGINEERING_DATA,
        "Elektrik Mühendisliği": ELECTRICAL_ENGINEERING_DATA,
        "Makine Mühendisliği": MECHANICAL_ENGINEERING_DATA,
    }

    total_upserted = 0
    for dept, data in datasets.items():
        print(f"\n🎓 {dept}: {len(data)} items")
        try:
            count = upsert_opportunities(data)
            total_upserted += count
            print(f"   ✅ Upserted {count} rows")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print(f"\n📊 Total static records upserted: {total_upserted}")
    return total_upserted


def seed_scraped_data():
    """Try to scrape live data from all sources for each department."""
    if not SCRAPERS_AVAILABLE:
        print("\n⚠️  Scrapers not available, skipping live scraping.")
        return 0

    print("\n" + "=" * 60)
    print("🌐  Scraping LIVE data from LinkedIn, Indeed, Udemy, Coursera...")
    print("=" * 60)

    total_scraped = 0

    for dept, roles in SCRAPE_TARGETS.items():
        print(f"\n🎓 Department: {dept}")
        print("-" * 40)

        for role in roles:
            all_opps = []
            print(f"\n  🔍 Searching: '{role}'")

            # LinkedIn
            try:
                jobs = scrape_linkedin_jobs(role, "Turkey", 5)
                all_opps.extend(jobs)
                print(f"    🔗 LinkedIn: {len(jobs)} results")
            except Exception as e:
                print(f"    ❌ LinkedIn: {e}")

            # Indeed
            try:
                jobs = scrape_indeed(role, "Turkey", 5)
                all_opps.extend(jobs)
                print(f"    🔍 Indeed: {len(jobs)} results")
            except Exception as e:
                print(f"    ❌ Indeed: {e}")

            # Udemy
            try:
                courses = scrape_udemy(role, 3)
                all_opps.extend(courses)
                print(f"    📚 Udemy: {len(courses)} results")
            except Exception as e:
                print(f"    ❌ Udemy: {e}")

            # Coursera
            try:
                courses = scrape_coursera(role, 3)
                all_opps.extend(courses)
                print(f"    🎓 Coursera: {len(courses)} results")
            except Exception as e:
                print(f"    ❌ Coursera: {e}")

            # Upsert batch
            if all_opps:
                try:
                    count = upsert_opportunities(all_opps)
                    total_scraped += count
                    print(f"    💾 Upserted {count} rows for '{role}'")
                except Exception as e:
                    print(f"    ❌ Upsert error: {e}")

            # Be polite to servers
            time.sleep(2)

    print(f"\n📊 Total scraped records upserted: {total_scraped}")
    return total_scraped


def print_final_stats():
    """Print final database statistics."""
    print("\n" + "=" * 60)
    print("📈  FINAL DATABASE STATISTICS")
    print("=" * 60)
    try:
        stats = get_stats()
        print(f"  Total records : {stats['total']}")
        print(f"  Active records: {stats['active']}")
        print(f"\n  By Type:")
        for t, c in stats.get("by_type", {}).items():
            print(f"    {t:>15}: {c}")
        print(f"\n  By Source:")
        for s, c in stats.get("by_source", {}).items():
            print(f"    {s:>15}: {c}")
    except Exception as e:
        print(f"  ❌ Could not fetch stats: {e}")


def main():
    print("🚀 Career Path Advisor — Engineering Database Seeder")
    print("   Departments: Bilgisayar, Elektrik, Makine Mühendisliği")
    print("=" * 60)

    # Step 1: Static data (guaranteed to work)
    static_count = seed_static_data()

    # Step 2: Live scraping (best-effort)
    scraped_count = seed_scraped_data()

    # Step 3: Final stats
    print_final_stats()

    print(f"\n✅ DONE! {static_count + scraped_count} total records upserted.")
    print("   Database is ready for Computer, Electrical, and Mechanical Engineering students.")


if __name__ == "__main__":
    main()
