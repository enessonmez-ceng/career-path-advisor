import os
import argparse
import random
from typing import List, Dict
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from tqdm import tqdm

# Set environment before loading utils
load_dotenv()

from graph.utils.chromadb_client import upsert_opportunities

# Set of providers for variety
PROVIDERS = [
    "Udemy", "Coursera", "edX", "Pluralsight", "LinkedIn Learning", 
    "DataCamp", "Udacity", "Codecademy", "Google", "AWS Training"
]

# Set of domains to generate synthetic courses
DOMAINS = {
    "Backend Development": {
        "skills": ["Python", "Java", "C#", "Go", "Node.js", "Django", "FastAPI", "Spring Boot", "Express", "SQL", "PostgreSQL", "MongoDB", "Redis", "REST API", "GraphQL"],
        "prefixes": ["Mastering", "Advanced", "The Complete Guide to", "Introduction to", "Build APIs with", "Backend Engineering with", "Scalable"]
    },
    "Frontend Development": {
        "skills": ["JavaScript", "TypeScript", "React", "Angular", "Vue", "Next.js", "Nuxt.js", "HTML/CSS", "Tailwind CSS", "SASS", "Redux", "Webhooks", "Web Performance"],
        "prefixes": ["Frontend Mastery:", "The Complete", "Modern", "Advanced", "Build UIs with", "Responsive Design with", "Fullstack"]
    },
    "Data Science & AI": {
        "skills": ["Python", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "OpenCV", "YOLO", "Machine Learning", "Deep Learning", "NLP", "LangChain", "RAG", "Data Visualization", "SQL"],
        "prefixes": ["Applied", "Deep Dive into", "Machine Learning with", "AI Engineering:", "Data Science Bootcamp:", "Generative AI using", "Computer Vision with"]
    },
    "DevOps & Cloud": {
        "skills": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins", "GitHub Actions", "Terraform", "Ansible", "Linux", "Bash", "System Administration", "Networking"],
        "prefixes": ["Cloud Computing with", "DevOps Essentials:", "Deploying Applications on", "Infrastructure as Code:", "Containerization using", "Certified Professional:"]
    },
    "Cybersecurity": {
        "skills": ["Network Security", "Penetration Testing", "Ethical Hacking", "Cryptography", "Linux", "Wireshark", "Burp Suite", "OWASP", "Information Security", "Incident Response"],
        "prefixes": ["Ethical Hacking:", "Cybersecurity Defense against", "Introduction to", "Advanced Network Security and"]
    },
    "Soft Skills & Management": {
        "skills": ["Agile", "Scrum", "Project Management", "Leadership", "Communication", "Time Management", "Problem Solving", "Conflict Resolution", "Product Management"],
        "prefixes": ["Mastering", "Essential", "The Complete Guide to", "Effective", "Executive"]
    }
}


def generate_synthetic_courses(num_courses: int) -> List[Dict]:
    """Generates a list of synthetic course opportunities."""
    courses = []
    course_id = 1
    
    # Generate around the desired number (exact count is not critical)
    for _ in range(num_courses):
        domain_name = random.choice(list(DOMAINS.keys()))
        domain_info = DOMAINS[domain_name]
        
        provider = random.choice(PROVIDERS)
        prefix = random.choice(domain_info["prefixes"])
        
        # Pick 2-5 skills for the course focus
        num_skills = random.randint(2, 5)
        course_skills = random.sample(domain_info["skills"], num_skills)
        
        # Build Title
        main_skill = course_skills[0]
        title = f"{prefix} {main_skill}"
        if random.random() > 0.5 and len(course_skills) > 1:
            title += f" and {course_skills[1]}"
            
        # Build Description
        levels = ["Beginner", "Intermediate", "Advanced", "All Levels"]
        level = random.choice(levels)
        hours = random.randint(3, 60)
        
        desc = (
            f"This comprehensive course from {provider} is designed for {level} students. "
            f"You will learn practical skills covering {', '.join(course_skills)}. "
            f"By the end of this {hours}-hour course, you will be proficient in {main_skill} "
            f"and ready to apply your knowledge in real-world scenarios."
        )
        
        # Random date within the last 2 years
        days_ago = random.randint(0, 730)
        posted_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        course_data = {
            "type": "course",
            "title": title,
            "provider": provider,
            "url": f"https://www.{provider.lower().replace(' ', '')}.com/course/synthetic-{course_id}",
            "description": desc,
            "required_skills": course_skills,
            "location": "Online",
            "posted_date": posted_date,
            "source": "synthetic_seed"
        }
        courses.append(course_data)
        course_id += 1
        
    return courses


def main():
    parser = argparse.ArgumentParser(description="Seed synthetic courses into ChromaDB")
    parser.add_argument("--count", type=int, default=300, help="Number of synthetic courses to generate (default: 300)")
    parser.add_argument("--no-embed", action="store_true", help="Skip generating AI embeddings (faster, but degrades semantic search quality)")
    args = parser.parse_args()
    
    print(f"Generating {args.count} synthetic courses...")
    courses = generate_synthetic_courses(args.count)
    
    print(f"Generated {len(courses)} courses. Preparing to upsert to ChromaDB...")
    
    if args.no_embed:
        print("[WARNING] Skipping embeddings. Search quality will degrade.")
        # Temporarily mock the embedding function in the client before we upsert
        import graph.utils.chromadb_client as client
        orig_get = client._get_embedding_service
        def _mock_get():
            svc = orig_get()
            return {"embed": lambda x: None, "text": svc["text"]}
        client._get_embedding_service = _mock_get

    # Pre-warm embedding initialization if needed
    from graph.utils.chromadb_client import _get_embedding_service
    _get_embedding_service()
    
    # Batch upsert
    batch_size = 50
    total_upserted = 0
    
    with tqdm(total=len(courses), desc="Upserting Courses") as pbar:
        for i in range(0, len(courses), batch_size):
            batch = courses[i:i+batch_size]
            try:
                upserted = upsert_opportunities(batch)
                total_upserted += upserted
            except Exception as e:
                print(f"\n[ERROR] Batch {i//batch_size} failed: {e}")
            pbar.update(len(batch))

    print(f"\n[DONE] Seeded {total_upserted} courses into ChromaDB")
    
    from graph.utils.chromadb_client import get_stats
    print(f"[STATS] {get_stats()}")


if __name__ == "__main__":
    main()
