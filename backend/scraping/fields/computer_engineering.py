"""
Computer Engineering (Bilgisayar Mühendisliği)
Search queries and static fallback data for scraping.
"""
from typing import List

from scraping.base_scraper import BrightDataClient


# ═══════════════════════════════════════════════════════════
# SEARCH QUERIES
# ═══════════════════════════════════════════════════════════
FIELD_NAME = "Bilgisayar Mühendisliği"

JOB_QUERIES = [
    "Software Engineer",
    "Software Engineer Intern",
    "Backend Developer",
    "Frontend Developer Intern",
    "Data Scientist",
    "Full Stack Developer",
    "DevOps Engineer",
    "Mobile Developer Intern",
    "AI ML Engineer",
    "Cybersecurity Analyst",
]

COURSE_QUERIES = [
    "Python programming",
    "Machine Learning",
    "React web development",
    "Cloud computing AWS",
    "Docker Kubernetes",
]


# ═══════════════════════════════════════════════════════════
# STATIC / FALLBACK DATA
# ═══════════════════════════════════════════════════════════
STATIC_DATA = [
    # ── Jobs / Internships ──
    {
        "type": "internship",
        "title": "Software Engineering Intern",
        "provider": "Google",
        "url": "https://careers.google.com/jobs/software-engineering-intern-2026",
        "description": "Join Google as a Software Engineering Intern. Work on large-scale distributed systems, develop production code in Python/Java/C++, and collaborate with world-class engineers.",
        "required_skills": ["Python", "Java", "C++", "Data Structures", "Algorithms"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-20",
        "source": "manual",
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
        "source": "manual",
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
        "source": "manual",
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
        "source": "manual",
    },
    {
        "type": "job",
        "title": "DevOps Engineer",
        "provider": "Hepsiburada",
        "url": "https://www.hepsiburada.com/careers/devops-engineer-2026",
        "description": "DevOps Engineer at Hepsiburada. Manage CI/CD pipelines, Kubernetes clusters, and cloud infrastructure on AWS.",
        "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Linux"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-10",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Mobile App Developer Intern",
        "provider": "Insider",
        "url": "https://useinsider.com/careers/mobile-developer-intern-2026",
        "description": "Mobile App Developer Intern at Insider. Develop cross-platform mobile applications using Flutter/Dart.",
        "required_skills": ["Flutter", "Dart", "Mobile Development", "REST API", "Git"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-19",
        "source": "manual",
    },
    {
        "type": "job",
        "title": "AI/ML Engineer",
        "provider": "Peak Games",
        "url": "https://www.peakgames.com/careers/ai-ml-engineer-2026",
        "description": "AI/ML Engineer at Peak Games. Build recommendation engines and predictive models for gaming analytics.",
        "required_skills": ["Python", "PyTorch", "Deep Learning", "MLOps", "SQL"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-14",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Frontend Developer Intern",
        "provider": "Yemeksepeti",
        "url": "https://www.yemeksepeti.com/kariyer/frontend-intern-2026",
        "description": "Frontend Developer Intern at Yemeksepeti. Build responsive web interfaces using React/Next.js.",
        "required_skills": ["React", "Next.js", "JavaScript", "CSS", "HTML", "Figma"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-21",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Yazılım Geliştirme Stajyeri",
        "provider": "Aselsan",
        "url": "https://www.aselsan.com/tr/kariyer/yazilim-staj-2026-1",
        "description": "Savunma sanayi projelerinde C++ ve Python kullanarak gömülü yazılım ve görüntü işleme algoritmaları geliştirme stajı.",
        "required_skills": ["C++", "Python", "Görüntü İşleme", "Linux", "Git"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-25",
        "source": "manual",
    },
    # ── Courses ──
    {
        "type": "course",
        "title": "The Complete Python Bootcamp From Zero to Hero",
        "provider": "Jose Portilla",
        "url": "https://www.udemy.com/course/complete-python-bootcamp/",
        "description": "Learn Python like a Professional: start from basics and go all the way to creating your own applications and games.",
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
        "description": "Andrew Ng's Machine Learning course. Learn supervised/unsupervised learning, neural networks, and practical ML techniques.",
        "required_skills": ["Python", "Machine Learning", "Linear Algebra"],
        "location": "Online",
        "posted_date": "",
        "source": "coursera",
    },
    {
        "type": "course",
        "title": "Docker & Kubernetes: The Practical Guide",
        "provider": "Academind",
        "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/",
        "description": "Learn Docker, Docker Compose, Multi-Container Projects, Deployment, and Kubernetes from scratch.",
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
        "description": "Harvard's introduction to computer science. Topics include algorithms, data structures, security, and web development.",
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
        "description": "Pass the AWS Solutions Architect Associate exam. Learn EC2, S3, RDS, VPC, Lambda, and more.",
        "required_skills": ["AWS", "Cloud Computing", "Networking"],
        "location": "Online",
        "posted_date": "",
        "source": "udemy",
    },
    # ── Certifications ──
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


# ═══════════════════════════════════════════════════════════
# SCRAPE FUNCTION
# ═══════════════════════════════════════════════════════════
def scrape(client: BrightDataClient, location: str = "Turkey", max_per_query: int = 10) -> List[dict]:
    """
    Scrape all Computer Engineering opportunities.

    Returns combined list of static data + live Bright Data results.
    """
    results = list(STATIC_DATA)  # Start with static fallback

    for query in JOB_QUERIES:
        try:
            jobs = client.scrape_linkedin_jobs(query, location, max_per_query)
            results.extend(jobs)
        except Exception as e:
            print(f"  ❌ Error scraping '{query}': {e}")

    return results
