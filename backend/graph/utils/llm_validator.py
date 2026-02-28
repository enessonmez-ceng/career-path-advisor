"""
LLM Output Validator — LLM Çıktısını Doğrulama ve Düzeltme
===========================================================

📚 KAYNAKLAR (Bunları oku/izle):
─────────────────────────────────
1. Levenshtein Distance (Edit Distance):
   https://en.wikipedia.org/wiki/Levenshtein_distance
   → İki string arasındaki minimum düzenleme sayısı. "Pytohn" → "Python" = 2 düzenleme.

2. RapidFuzz kütüphanesi:
   https://github.com/rapidfuzz/RapidFuzz
   → FuzzyWuzzy'nin hızlı versiyonu. String benzerliği için kullanılır.
   → pip install rapidfuzz

3. Pydantic Validation:
   https://docs.pydantic.dev/latest/
   → LLM çıktısını yapılandırılmış veriye çevirip doğrulama.

4. Guardrails AI:
   https://github.com/guardrails-ai/guardrails
   → LLM çıktısı için validation framework'ü. İleri okuma.

5. YouTube - "Validating LLM Output":
   https://www.youtube.com/results?search_query=validate+llm+output+python
   → LLM çıktı doğrulama best practice'leri.

AMAÇ:
─────
LLM her zaman doğru çıktı üretmez. Bu dosya:
  1. LLM'in çıkardığı skill'leri bilinen bir veritabanıyla karşılaştırır
  2. Yanlış yazılmış skill'leri düzeltir (fuzzy matching)
  3. Hallucination'ları (uydurma sonuçlar) tespit eder
  4. Çıktı formatını doğrular

Mülakatçıya: "LLM'e körü körüne güvenmiyorum, çıktısını doğruluyorum"
"""

from typing import List, Dict, Optional, Tuple


# ═══════════════════════════════════════════════════════════
# BİLİNEN SKİLL VERİTABANI
# ═══════════════════════════════════════════════════════════
# Bu listeyi genişletebilirsin. Amaç: LLM'in uydurduğu
# skill'leri yakalamak. "Quantumflux Programming" gibi
# bir şey gelirse, bu listede olmadığı için reddedilir.

KNOWN_SKILLS = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "c",
    "go", "rust", "ruby", "php", "swift", "kotlin", "r", "scala",
    "dart", "matlab", "perl", "lua", "haskell", "elixir",

    # Frontend
    "react", "vue", "angular", "svelte", "next.js", "nuxt.js",
    "html", "css", "sass", "tailwind", "bootstrap", "jquery",

    # Backend
    "node.js", "express", "django", "flask", "fastapi", "spring",
    "spring boot", "rails", "laravel", "asp.net", ".net",

    # Database
    "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle",
    "elasticsearch", "cassandra", "dynamodb", "supabase", "firebase",

    # DevOps & Cloud
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
    "jenkins", "github actions", "ci/cd", "nginx", "linux",

    # Data & AI
    "machine learning", "deep learning", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit-learn", "nlp", "computer vision",
    "langchain", "openai", "hugging face", "llm",

    # Tools
    "git", "github", "gitlab", "jira", "figma", "postman",
    "vs code", "intellij", "vim",

    # Soft Skills
    "communication", "teamwork", "leadership", "problem solving",
    "agile", "scrum", "project management",
}

# Yaygın yazım hataları → doğru karşılıkları
SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "node": "node.js",
    "react.js": "react",
    "vue.js": "vue",
    "angular.js": "angular",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "tf": "tensorflow",
    "sk-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "nextjs": "next.js",
    "fastapi": "fastapi",
}


# ═══════════════════════════════════════════════════════════
# 1. FUZZY MATCHING
# ═══════════════════════════════════════════════════════════

def fuzzy_find_skill(skill_name: str, threshold: int = 80) -> Optional[str]:
    """
    Yanlış yazılmış bir skill'i bilinen skill veritabanında ara.
    
    Önce alias'lara bak, sonra fuzzy match yap.
    
    Args:
        skill_name: LLM'in çıkardığı skill adı
        threshold: Minimum benzerlik skoru (0-100)
    
    Returns:
        Düzeltilmiş skill adı veya None
    """
    normalized = skill_name.lower().strip()

    # 1. Direkt eşleşme
    if normalized in KNOWN_SKILLS:
        return normalized

    # 2. Alias kontrolü
    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]

    # 3. Fuzzy match (RapidFuzz gerekli)
    try:
        from rapidfuzz import fuzz, process
        
        result = process.extractOne(
            normalized,
            KNOWN_SKILLS,
            scorer=fuzz.ratio,
            score_cutoff=threshold,
        )
        if result:
            return result[0]  # (match, score, index)
    except ImportError:
        # RapidFuzz yoksa basit contains kontrolü (min 4 karakter)
        if len(normalized) >= 4:
            for known in KNOWN_SKILLS:
                if len(known) >= 4 and (normalized in known or known in normalized):
                    return known

    return None


# ═══════════════════════════════════════════════════════════
# 2. LLM ÇIKTI DOĞRULAMA
# ═══════════════════════════════════════════════════════════

def validate_skills(
    llm_skills: List[str],
    strict: bool = False,
) -> Dict:
    """
    LLM'in çıkardığı skill listesini doğrula ve düzelt.
    
    Args:
        llm_skills: LLM'in CV'den çıkardığı skill'ler
        strict: True ise bilinmeyen skill'leri tamamen at
    
    Returns:
        {
            "validated": [...],     # Doğrulanmış skill'ler
            "corrected": [...],     # Düzeltilmiş skill'ler (orijinal → düzeltilmiş)
            "rejected": [...],      # Reddedilen (bilinmeyen) skill'ler
            "confidence": 0.85,     # Doğrulama güven skoru
        }
    """
    validated = []
    corrected = []
    rejected = []

    for skill in llm_skills:
        normalized = skill.lower().strip()
        
        if not normalized or len(normalized) < 2:
            rejected.append({"original": skill, "reason": "Too short"})
            continue

        if len(normalized) > 50:
            rejected.append({"original": skill, "reason": "Too long (probably a sentence)"})
            continue

        # Doğrudan eşleşme
        if normalized in KNOWN_SKILLS:
            validated.append(normalized)
            continue

        # Alias
        if normalized in SKILL_ALIASES:
            correct = SKILL_ALIASES[normalized]
            validated.append(correct)
            corrected.append({"original": skill, "corrected": correct})
            continue

        # Fuzzy match
        match = fuzzy_find_skill(normalized)
        if match:
            validated.append(match)
            if match != normalized:
                corrected.append({"original": skill, "corrected": match})
            continue

        # Bilinmeyen skill
        if strict:
            rejected.append({"original": skill, "reason": "Unknown skill"})
        else:
            # Strict değilse kabul et ama işaretle
            validated.append(normalized)
            corrected.append({"original": skill, "corrected": normalized, "note": "Unverified"})

    # Duplikasyonları temizle
    validated = list(dict.fromkeys(validated))

    # Güven skoru
    total = len(llm_skills)
    if total > 0:
        direct_matches = total - len(corrected) - len(rejected)
        confidence = direct_matches / total
    else:
        confidence = 0.0

    return {
        "validated": validated,
        "corrected": corrected,
        "rejected": rejected,
        "confidence": round(confidence, 2),
        "stats": {
            "input_count": total,
            "validated_count": len(validated),
            "corrected_count": len(corrected),
            "rejected_count": len(rejected),
        }
    }


# ═══════════════════════════════════════════════════════════
# 3. OPPORTUNITY VALIDATION
# ═══════════════════════════════════════════════════════════

def validate_opportunity(opportunity: Dict) -> Dict:
    """
    LLM'in önerdiği bir ilanı/kursu doğrula.
    
    Kontroller:
    - URL geçerli mi?
    - Başlık mantıklı mı?
    - Duplikasyon var mı?
    
    Returns:
        {"is_valid": bool, "issues": [...], "cleaned": {...}}
    """
    issues = []
    cleaned = dict(opportunity)

    # URL kontrolü
    url = opportunity.get("url", "")
    if not url:
        issues.append("Missing URL")
    elif not url.startswith(("http://", "https://")):
        issues.append(f"Invalid URL format: {url}")

    # Başlık kontrolü
    title = opportunity.get("title", "")
    if not title:
        issues.append("Missing title")
    elif len(title) < 5:
        issues.append("Title too short")
    elif len(title) > 200:
        cleaned["title"] = title[:200]
        issues.append("Title truncated")

    # Skill validation
    skills = opportunity.get("required_skills", [])
    if skills:
        result = validate_skills(skills, strict=False)
        cleaned["required_skills"] = result["validated"]
        if result["rejected"]:
            issues.append(f"Rejected {len(result['rejected'])} invalid skills")

    is_valid = len([i for i in issues if "Missing" in i]) == 0

    return {
        "is_valid": is_valid,
        "issues": issues,
        "cleaned": cleaned,
    }
