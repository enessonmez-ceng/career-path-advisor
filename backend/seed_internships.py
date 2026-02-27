"""
Seed Internships
Populates the Supabase database specifically with INTERNSHIP opportunities for:
  - Bilgisayar Mühendisliği (Computer Engineering)
  - Elektrik Mühendisliği (Electrical Engineering)
  - Makine Mühendisliği (Mechanical Engineering)

Usage:
    python seed_internships.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from graph.utils.supabase_client import upsert_opportunities, get_stats

try:
    from graph.utils.job_scraper import scrape_linkedin_jobs
    from graph.utils.indeed_scraper import scrape_indeed
    SCRAPERS_AVAILABLE = True
except ImportError:
    SCRAPERS_AVAILABLE = False
    print("⚠️  Scrapers not available, using static data only.")


# ═══════════════════════════════════════════════
# STATIC / FALLBACK INTERNSHIP DATA
# ═══════════════════════════════════════════════

COMPUTER_INTERNSHIPS = [
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
    {
        "type": "internship",
        "title": "Data Engineering Intern",
        "provider": "Garanti BBVA Teknoloji",
        "url": "https://garantibbvateknoloji.com.tr/data-engineering-intern-2026",
        "description": "Büyük veri ortamında ETL süreçleri tasarımı, Hadoop ve Spark kullanarak veri boru hatları oluşturma. SQL ve Python bilgisi şarttır.",
        "required_skills": ["SQL", "Python", "Hadoop", "Spark", "ETL"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-24",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Cloud Computing stajyeri (AWS/Azure)",
        "provider": "KoçDigital",
        "url": "https://kocdigital.com.tr/cloud-intern-2026",
        "description": "KoçDigital bulut altyapı ekibinde staj. IaaS/PaaS yönetimi, Docker konteynerleştirme ve CI/CD süreçlerine destek.",
        "required_skills": ["AWS", "Azure", "Docker", "DevOps", "Linux"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-20",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Game Developer Intern",
        "provider": "Dream Games",
        "url": "https://dreamgames.com/careers/game-dev-intern",
        "description": "Unity 3D ve C# kullanarak mobil oyun geliştirme süreçlerine dahil olma şansı. En iyi performans optimizasyonlarını öğrenin.",
        "required_skills": ["Unity", "C#", "Mobile Development", "Algorithms"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-26",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Web Developer Stajyer",
        "provider": "Papara",
        "url": "https://papara.com/careers/web-intern-26",
        "description": "Milyonlarca kullanıcısı olan Papara web platformunda React ve TypeScript ile arayüz geliştirme stajı.",
        "required_skills": ["React", "TypeScript", "HTML5", "CSS3", "Git"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-21",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Cyber Security Intern",
        "provider": "Picnic Security",
        "url": "https://picnicsecurity.com/intern",
        "description": "Sızma testleri, güvenlik zafiyet analizi ve ağ güvenliği alanlarında stajyer alınacaktır.",
        "required_skills": ["Penetration Testing", "Linux", "Network Security", "Python"],
        "location": "Remote, Turkey",
        "posted_date": "2026-02-27",
        "source": "manual",
    },
]

ELECTRICAL_INTERNSHIPS = [
    {
        "type": "internship",
        "title": "Otomasyon Sistemleri Stajyeri",
        "provider": "BOSCH Sanayi",
        "url": "https://careers.bosch.com/tr/automation-intern-bursa",
        "description": "Endüstri 4.0 dönüşüm projelerinde, PLC programlama ve fabrika otomasyon sistemleri tasarımı üzerine uzun dönem staj.",
        "required_skills": ["PLC", "Automation", "Siemens TIA Portal", "Endüstri 4.0"],
        "location": "Bursa, Turkey",
        "posted_date": "2026-02-25",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Hardware Design Intern",
        "provider": "Baykar Makina",
        "url": "https://kariyer.baykartech.com/hardware-design-intern",
        "description": "İHA/SİHA aviyonik sistem donanım tasarımı. Altium ile PCB tasarımı ve EMI/EMC uyumluluk testleri.",
        "required_skills": ["PCB Design", "Altium", "Electronics", "Hardware Testing"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-24",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Elektrik Dağıtım Stajyeri",
        "provider": "Enerjisa",
        "url": "https://www.enerjisa.com.tr/kariyer/dagitim-staj26",
        "description": "Şebeke operasyonları, trafo bakımları ve OG/AG enerji dağıtım projelerinde saha ve ofis stajı.",
        "required_skills": ["Power Distribution", "AutoCAD", "High Voltage", "Electrical Design"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-18",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Telecommunication Engineering Intern",
        "provider": "Türk Telekom",
        "url": "https://turktelekomkariyer.com.tr/telecom-intern",
        "description": "5G altyapı çalışmaları, fiber optik ağ planlaması ve RF haberleşme alanında çalışma imkanı.",
        "required_skills": ["RF Engineering", "Telecommunications", "Network Planning", "5G"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-22",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Batarya Sistemleri Stajyeri",
        "provider": "Siro Energy",
        "url": "https://siro.energy/careers/internship",
        "description": "Elektrikli araçlar için Li-ion batarya hücresi üretimi ve batarya yönetim sistemi (BMS) konularında Ar-Ge stajı.",
        "required_skills": ["BMS", "Battery Systems", "Power Electronics", "MATLAB"],
        "location": "Bursa, Turkey",
        "posted_date": "2026-02-26",
        "source": "manual",
    },
]

MECHANICAL_INTERNSHIPS = [
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
    {
        "type": "internship",
        "title": "Havacılık Motorları Stajyeri",
        "provider": "TEI (TUSAŞ Engine Industries)",
        "url": "https://tei.com.tr/kariyer/aerospace-engine-intern",
        "description": "Havacılık motor parçalarının üretim mühendisliği ve aerodinamik test süreçleri departmanlarında uzun dönem staj.",
        "required_skills": ["Aerodynamics", "Thermodynamics", "Manufacturing", "Siemens NX"],
        "location": "Eskişehir, Turkey",
        "posted_date": "2026-02-24",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Mekanik Tesisat Proje Stajyeri",
        "provider": "Rönesans Holding",
        "url": "https://ronesanskariyer.com/mekanik-proje-staj",
        "description": "Hastane ve AVM projelerinde HVAC, sıhhi tesisat ve yangın sistemlerinin proje çizimi (Revit/AutoCAD) stajı.",
        "required_skills": ["HVAC", "Revit MEP", "AutoCAD", "Plumbing Design"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-15",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Uzay ve Uydu Mekaniği Stajyeri",
        "provider": "TÜBİTAK UZAY",
        "url": "https://uzay.tubitak.gov.tr/tr/kariyer/uydu-mekanik-staj",
        "description": "Uzay araçları yapısal tasarımı, termal analizi ve titreşim testleri üzerine laboratuvar destek stajı.",
        "required_skills": ["Space Mechanics", "Thermal Analysis", "Vibration Testing", "SolidWorks"],
        "location": "Ankara, Turkey",
        "posted_date": "2026-02-20",
        "source": "manual",
    },
    {
        "type": "internship",
        "title": "Robotik ve Mekatronik Stajyeri",
        "provider": "Altınay Robot Teknolojileri",
        "url": "https://altinay-robotics.com/internship",
        "description": "Endüstriyel robotik hücre tasarımı, gripper (tutucu) mekanizma dizaynı ve kinematik analiz stajı.",
        "required_skills": ["Robotics", "Kinematics", "SolidWorks", "Mechatronics"],
        "location": "Istanbul, Turkey",
        "posted_date": "2026-02-27",
        "source": "manual",
    },
]

# ═══════════════════════════════════════════════
# SCRAPING TARGETS (ONLY INTERNSHIPS)
# ═══════════════════════════════════════════════
INTERNSHIP_TARGETS = {
    "Bilgisayar Mühendisliği": [
        "Software Engineering Intern",
        "Yazılım Stajyer",
        "Data Science Intern",
        "Bilgisayar Mühendisliği Staj",
        "IT Intern",
        "Frontend Intern",
        "Backend Intern",
    ],
    "Elektrik Mühendisliği": [
        "Electrical Engineering Intern",
        "Elektrik Elektronik Stajyer",
        "Hardware Intern",
        "Otomasyon Stajyer",
        "Elektrik Mühendisliği Staj",
    ],
    "Makine Mühendisliği": [
        "Mechanical Engineering Intern",
        "Makine Mühendisliği Staj",
        "Üretim Stajyer",
        "Ar-Ge Stajyer",
        "CATIA Stajyer",
    ],
}


def seed_static_internships():
    print("\n" + "=" * 60)
    print("📦  Seeding STATIC INTERNSHIPS into Supabase...")
    print("=" * 60)

    datasets = {
        "Bilgisayar": COMPUTER_INTERNSHIPS,
        "Elektrik": ELECTRICAL_INTERNSHIPS,
        "Makine": MECHANICAL_INTERNSHIPS,
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

    return total_upserted


def scrape_live_internships():
    if not SCRAPERS_AVAILABLE:
        print("\n⚠️  Scrapers not available.")
        return 0

    print("\n" + "=" * 60)
    print("🌐  Scraping LIVE INTERNSHIPS from LinkedIn & Indeed...")
    print("=" * 60)

    total_scraped = 0

    for dept, roles in INTERNSHIP_TARGETS.items():
        print(f"\n🎓 Department: {dept}")
        print("-" * 40)

        for role in roles:
            # ONLY internships
            search_query = role if "intern" in role.lower() or "staj" in role.lower() else f"{role} Intern"
            all_opps = []
            print(f"\n  🔍 Searching for: '{search_query}'")

            # LinkedIn
            try:
                # Get more results for LinkedIn
                jobs = scrape_linkedin_jobs(search_query, "Turkey", 15)
                # Ensure they are marked as internship
                for j in jobs:
                    j["type"] = "internship"
                all_opps.extend(jobs)
                print(f"    🔗 LinkedIn: {len(jobs)} results")
            except Exception as e:
                print(f"    ❌ LinkedIn: {e}")

            # Indeed
            try:
                jobs = scrape_indeed(search_query, "Turkey", 10)
                for j in jobs:
                    j["type"] = "internship"
                all_opps.extend(jobs)
                print(f"    🔍 Indeed: {len(jobs)} results")
            except Exception as e:
                print(f"    ❌ Indeed: {e}")

            # Upsert
            if all_opps:
                try:
                    count = upsert_opportunities(all_opps)
                    total_scraped += count
                    print(f"    💾 Upserted {count} rows")
                except Exception as e:
                    print(f"    ❌ Upsert error: {e}")

            # Politeness delay
            time.sleep(3)

    return total_scraped


def main():
    print("🚀 Career Path Advisor — INTERNSHIP Database Seeder")
    print("=" * 60)

    static_count = seed_static_internships()
    scraped_count = scrape_live_internships()

    print("\n" + "=" * 60)
    print("📈  CURRENT DATABASE STATISTICS")
    print("=" * 60)
    try:
        stats = get_stats()
        print(f"  Total records : {stats['total']}")
        print(f"  Active records: {stats['active']}")
        print(f"\n  By Type:")
        for t, c in stats.get("by_type", {}).items():
            print(f"    {t:>15}: {c}")
    except Exception as e:
        print(f"  ❌ Could not fetch stats: {e}")

    print(f"\n✅ DONE! {static_count + scraped_count} new INTERNSHIP records added.")

if __name__ == "__main__":
    main()
