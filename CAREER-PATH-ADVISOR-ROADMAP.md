# 🎯 Career Path Advisor - Proje Roadmap

## 📋 Proje Özeti

**Proje Adı:** Career Path Advisor  
**Açıklama:** Kullanıcının yüklediği CV, portfolyo veya LinkedIn profiline göre staj, etkinlik, kurs ve yetenek geliştirme önerileri sunan akıllı kariyer asistanı.

**Neden Bu Proje CV'de Dikkat Çeker?**
- 🔥 LangGraph'ın tüm advanced patternlerini kullanıyor (ReAct, Reflection, Self-Corrective RAG)
- 📄 Document parsing & NLP yetenekleri gösteriyor
- 🎯 Kişiselleştirme algoritmaları içeriyor
- 🧠 Multi-agent architecture ile skill gap analizi
- 🌐 Real-time veri entegrasyonu (staj/kurs API'leri)
- 🎨 Modern UI ile profesyonel görünüm

---

## 🎯 Özellikler

### Temel Özellikler
- [ ] Kullanıcı CV/döküman yükler (PDF, DOCX, TXT)
- [ ] CV'den beceriler, deneyimler ve eğitim bilgisi çıkarılır
- [ ] Mevcut yetenekler analiz edilir
- [ ] Eksik yetenekler (skill gap) tespit edilir
- [ ] Uygun staj fırsatları önerilir
- [ ] Kişiye özel kurs önerileri sunulur
- [ ] Etkinlik ve workshop önerileri yapılır
- [ ] Detaylı kariyer gelişim raporu oluşturulur

### İleri Seviye Özellikler
- [ ] LinkedIn profil URL'si ile analiz
- [ ] Farklı kariyer yolları için karşılaştırmalı öneri
- [ ] Zaman bazlı gelişim planı (3-6-12 ay)
- [ ] PDF olarak rapor indirme
- [ ] Öneri geçmişi kaydetme
- [ ] Canlı progress gösterimi (streaming)

---

## 🏗️ Teknik Mimari

### Tech Stack

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Python + FastAPI |
| **AI Framework** | LangGraph + LangChain |
| **LLM** | OpenAI GPT-4o-mini |
| **Document Parsing** | PyMuPDF, python-docx, unstructured |
| **Web Search** | Tavily API (staj/kurs araması) |
| **Frontend** | Next.js / Streamlit |
| **Deployment** | Vercel (Frontend) + Railway/Render (Backend) |
| **Database** | Supabase (kullanıcı geçmişi, opsiyonel) |

### LangGraph Workflow

```
┌─────────────────┐
│   CV Parser     │ → Döküman analizi, bilgi çıkarma
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Skill Extractor│ → Yetenekleri kategorize et
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gap Analyzer   │ → Eksik yetenekleri tespit et
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Opportunity     │ → Staj, kurs, etkinlik ara
│   Researcher    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Matcher &      │ → Fırsatları değerlendir, skorla
│    Grader       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Roadmap        │ → Kişisel gelişim planı oluştur
│   Generator     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Reviewer      │ → Eleştir, geliştir (Reflection)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Publisher     │ → Final öneri raporu
└─────────────────┘
```

---

## 📁 Proje Yapısı

```
career-path-advisor/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── graph/
│       ├── __init__.py
│       ├── graph.py            # Ana workflow
│       ├── state.py            # State tanımı
│       ├── consts.py           # Sabitler
│       ├── chains/
│       │   ├── __init__.py
│       │   ├── cv_parser.py    # CV parsing & extraction
│       │   ├── skill_extractor.py  # Yetenek çıkarma
│       │   ├── gap_analyzer.py     # Eksik yetenek analizi
│       │   ├── opportunity_researcher.py  # Fırsat araştırma
│       │   ├── matcher.py      # Eşleştirme & skorlama
│       │   ├── roadmap_gen.py  # Gelişim planı
│       │   └── reviewer.py     # Eleştiri & revizyon
│       ├── nodes/
│       │   ├── __init__.py
│       │   ├── parse.py
│       │   ├── extract.py
│       │   ├── analyze.py
│       │   ├── research.py
│       │   ├── match.py
│       │   ├── generate.py
│       │   └── review.py
│       └── utils/
│           ├── __init__.py
│           ├── document_loader.py  # PDF/DOCX yükleme
│           └── skill_database.py   # Yetenek kategorileri
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── upload/
│   │   └── api/
│   ├── components/
│   │   ├── FileUploader.tsx
│   │   ├── SkillsChart.tsx
│   │   └── RecommendationCard.tsx
│   └── package.json
├── data/
│   ├── skills_taxonomy.json    # Yetenek kategorileri
│   └── industry_requirements.json  # Sektör gereksinimleri
├── README.md
├── LICENSE
└── .github/
    └── workflows/
        └── deploy.yml
```

---

## 📅 Geliştirme Planı

### Hafta 1: CV Parsing & Skill Extraction
- [✓] Proje klasörü oluştur
- [✓] Poetry/pip ile dependency kurulumu
- [✓] State ve consts tanımla
- [✓] Document loader oluştur (PDF, DOCX desteği)
- [✓] CV Parser chain (bilgi çıkarma)
- [✓] Skill Extractor chain (yetenek kategorileme)
- [ ] Temel workflow'u test et

### Hafta 2: Gap Analysis & Opportunity Research
- [ ] Skills taxonomy JSON oluştur
- [✓] Gap Analyzer chain (eksik yetenek tespiti)
- [ ] Opportunity Researcher chain (Tavily entegrasyonu)
- [ ] Matcher chain (fırsat skorlama)
- [ ] Hallucination check ekle
- [ ] End-to-end test yaz

### Hafta 3: Roadmap Generation & API
- [ ] Roadmap Generator chain
- [ ] Reviewer chain (Reflection pattern)
- [ ] FastAPI endpoint'leri
- [ ] File upload endpoint
- [ ] Streaming response
- [ ] Error handling

### Hafta 4: Frontend & Deploy
- [ ] Next.js/Streamlit UI
- [ ] File upload komponenti
- [ ] Skills visualization (chart)
- [ ] Recommendation cards
- [ ] Backend deploy (Railway/Render)
- [ ] Frontend deploy (Vercel)
- [ ] README.md ve dokümantasyon

---

## 🔧 Başlangıç Adımları

### 1. Proje Oluştur
```bash
mkdir career-path-advisor
cd career-path-advisor
mkdir backend frontend data
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Dependencies
```bash
pip install langchain langchain-openai langgraph langchain-tavily
pip install fastapi uvicorn python-dotenv
pip install pydantic python-multipart
pip install pymupdf python-docx unstructured
pip install pandas
```

### 3. .env Dosyası
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### 4. İlk Çalıştırma
```bash
python main.py
```

---

## 📊 State Tanımı

```python
from typing import List, TypedDict, Optional
from enum import Enum

class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Skill(TypedDict):
    name: str
    category: str  # "technical", "soft", "language", "tool"
    level: SkillLevel
    years_experience: Optional[float]

class Experience(TypedDict):
    title: str
    company: str
    duration: str
    description: str
    skills_used: List[str]

class Education(TypedDict):
    degree: str
    field: str
    institution: str
    year: Optional[int]

class Opportunity(TypedDict):
    type: str  # "internship", "course", "event", "certification"
    title: str
    provider: str
    url: str
    description: str
    required_skills: List[str]
    match_score: float
    reason: str

class SkillGap(TypedDict):
    skill: str
    current_level: Optional[SkillLevel]
    target_level: SkillLevel
    priority: str  # "high", "medium", "low"
    recommendation: str

class CareerState(TypedDict):
    # Input
    document_content: str           # Ham döküman içeriği
    document_type: str              # "cv", "resume", "linkedin"
    target_role: Optional[str]      # Hedef pozisyon (opsiyonel)
    
    # Extracted Info
    name: str
    email: Optional[str]
    current_skills: List[Skill]
    experiences: List[Experience]
    education: List[Education]
    
    # Analysis
    skill_gaps: List[SkillGap]
    strengths: List[str]
    areas_to_improve: List[str]
    
    # Recommendations
    internship_recommendations: List[Opportunity]
    course_recommendations: List[Opportunity]
    event_recommendations: List[Opportunity]
    certification_recommendations: List[Opportunity]
    
    # Output
    development_roadmap: str        # 3-6-12 aylık plan
    draft_report: str               # İlk taslak
    critique: str                   # Eleştiri
    final_report: str               # Final rapor
    iteration: int                  # Revizyon sayısı
```

---

## 🎨 UI Tasarım Önerileri

### Ana Sayfa
- Modern, minimal tasarım
- Gradient arka plan (kariyer temalı renkler)
- Drag & drop file upload alanı
- "CV'nizi yükleyin" başlığı
- Desteklenen formatlar: PDF, DOCX, TXT
- Opsiyonel: Hedef pozisyon seçimi

### Sonuç Sayfası
- **Üst Panel:** Profil özeti (isim, mevcut yetenekler)
- **Sol Panel:** 
  - Skill Chart (radar/bar chart)
  - Güçlü yönler
  - Gelişim alanları
- **Sağ Panel:**
  - Tab'lı öneri listesi (Stajlar, Kurslar, Etkinlikler)
  - Her öneri için match score
- **Alt Panel:** 
  - Kişisel gelişim yol haritası (timeline)
  - Export butonları (PDF, Markdown)

---

## 📝 README.md İçeriği

```markdown
# 🎯 Career Path Advisor

An AI-powered career development assistant that analyzes your CV/resume and provides
personalized recommendations for internships, courses, events, and skill development.

## Features
- 📄 CV/Resume parsing (PDF, DOCX support)
- 🔍 Automatic skill extraction and categorization
- 📊 Skill gap analysis
- 💼 Personalized internship recommendations
- 📚 Course and certification suggestions
- 🗓️ Event and workshop recommendations
- 🗺️ Custom career development roadmap
- 🔄 Self-improvement through reflection

## Demo
[Live Demo](https://your-demo-link.vercel.app)

## Tech Stack
- LangGraph for agentic workflows
- FastAPI for backend
- Next.js for frontend
- OpenAI GPT-4o for LLM
- Tavily for opportunity search
- PyMuPDF & python-docx for document parsing

## Quick Start
...

## Architecture
...

## License
MIT
```

---

## 🏆 CV'de Nasıl Sunulur?

### Proje Açıklaması (Kısa)
> **Career Path Advisor** - LangGraph tabanlı, CV analizi yaparak kişiselleştirilmiş kariyer önerileri sunan akıllı asistan. Multi-agent architecture ile skill gap analizi, staj/kurs/etkinlik eşleştirme ve gelişim yol haritası oluşturma.

### Bullet Points
- Built an AI-powered career advisor using LangGraph with multi-agent architecture
- Implemented CV parsing and NLP-based skill extraction from PDF/DOCX documents
- Developed skill gap analysis and personalized opportunity matching algorithms
- Created REST API with FastAPI and modern UI with Next.js featuring file upload
- Integrated real-time internship, course, and event search using Tavily API
- Deployed to production with automated CI/CD pipeline

---

## 🔗 Faydalı Linkler

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [PyMuPDF Docs](https://pymupdf.readthedocs.io/)
- [python-docx Docs](https://python-docx.readthedocs.io/)
- [Tavily API](https://tavily.com/)
- [Vercel Deployment](https://vercel.com/)
- [Railway Deployment](https://railway.app/)

---

## ✅ Başarı Kriterleri

Proje tamamlandığında şunlar olmalı:
- [ ] GitHub'da public repo
- [ ] Detaylı README.md
- [ ] Canlı demo linki
- [ ] En az 3 farklı CV ile test
- [ ] Farklı dosya formatları desteği (PDF, DOCX)
- [ ] Clean code & proper structure
- [ ] CI/CD pipeline
- [ ] Skill visualization (chart)

---

## 🎯 Örnek Kullanım Senaryoları

### Senaryo 1: Bilgisayar Mühendisliği Öğrencisi
**Input:** 3. sınıf öğrencisinin CV'si (Python, Java, SQL bilgisi)
**Output:**
- Staj: Backend Developer Intern @ Startup X
- Kurs: AWS Cloud Practitioner, Docker Fundamentals
- Etkinlik: Google Developer Groups Meetup
- Roadmap: 3 ayda cloud skills, 6 ayda DevOps basics

### Senaryo 2: Kariyer Değişikliği
**Input:** 5 yıllık muhasebeci, yazılıma geçmek istiyor
**Output:**
- Kurs: CS50, Python for Beginners
- Etkinlik: Tech Career Fair
- Sertifika: Google IT Support Professional
- Roadmap: 6 ayda frontend basics, 12 ayda junior developer ready

### Senaryo 3: Yeni Mezun
**Input:** Yeni mezun, az deneyim
**Output:**
- Staj: Entry-level positions listesi
- Kurs: Soft skills, interview preparation
- Etkinlik: Networking events, hackathons
- Roadmap: Portfolio oluşturma, GitHub aktivitesi
