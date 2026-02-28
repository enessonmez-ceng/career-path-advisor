"""
Skill Matcher — Kendi Eşleştirme Algoritman (LLM Kullanmadan)
=============================================================

📚 KAYNAKLAR (Bunları oku/izle):
─────────────────────────────────
1. Jaccard Similarity:
   https://en.wikipedia.org/wiki/Jaccard_index
   → İki kümenin benzerliğini ölçer: |A ∩ B| / |A ∪ B|

2. TF-IDF (Term Frequency - Inverse Document Frequency):
   https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
   → Kelimelerin önemini ölçer. Sık geçen ama her yerde olan kelimeler (ve, bir) düşük skor alır.

3. Cosine Similarity:
   https://en.wikipedia.org/wiki/Cosine_similarity
   → İki vektör arasındaki açıyı ölçer. Embedding'lerle birlikte kullanılır.

4. FuzzyWuzzy / RapidFuzz (Fuzzy String Matching):
   https://github.com/seatgeek/fuzzywuzzy
   → "Pytohn" ile "Python" arasındaki benzerliği bulur (Levenshtein distance).

5. Scikit-learn metrikleri:
   https://scikit-learn.org/stable/modules/metrics.html
   → precision, recall, f1-score — algoritmanın başarısını ölçmek için.

6. YouTube - "Build a Job Recommender System":
   https://www.youtube.com/results?search_query=build+job+recommender+python
   → Benzer projeler nasıl yapılmış, fikir almak için.

AMAÇ:
─────
Bu dosyada LLM KULLANMADAN kendi skill-job matching algoritmanı yazacaksın.
İki ana yöntem:
  1. Set-based matching (Jaccard, Overlap coefficient)
  2. TF-IDF + Cosine similarity

Sonra LLM skoruyla kendi skorunu karşılaştırıp hangisinin daha iyi olduğunu göstereceksin.
Bu, mülakatçıya "sadece API çağırmadım, kendi algoritmamı da yazdım ve karşılaştırdım" demen için.
"""

from typing import List, Dict, Optional
from collections import Counter
import math


# ═══════════════════════════════════════════════════════════
# 1. SET-BASED MATCHING (Basit ama etkili)
# ═══════════════════════════════════════════════════════════

def jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Jaccard benzerlik indeksi: |A ∩ B| / |A ∪ B|
    
    Örnek:
        user_skills = {"python", "react", "sql"}
        job_skills  = {"python", "java", "sql", "docker"}
        jaccard = 2/5 = 0.40
    """
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def overlap_coefficient(set_a: set, set_b: set) -> float:
    """
    Overlap katsayısı: |A ∩ B| / min(|A|, |B|)
    Küçük kümenin ne kadarının örtüştüğünü ölçer.
    
    Neden Jaccard'dan farklı:
        Kullanıcının 3 skill'i var, iş ilanı 10 skill istiyor.
        Jaccard düşük çıkar ama overlap yüksek olabilir
        (çünkü kullanıcının bildiği 3 skill'in hepsi ilana uygun olabilir).
    """
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    return len(intersection) / min(len(set_a), len(set_b))


def skill_coverage(user_skills: set, required_skills: set) -> float:
    """
    İlanın istediği skill'lerin ne kadarını kullanıcı karşılıyor?
    
    Formül: |user ∩ required| / |required|
    
    Bu en pratik metrik:
        required = {"python", "react", "docker", "sql"}
        user     = {"python", "sql", "javascript"}
        coverage = 2/4 = 0.50 → kullanıcı ilanın %50'sini karşılıyor
    """
    if not required_skills:
        return 0.0
    matched = user_skills & required_skills
    return len(matched) / len(required_skills)


# ═══════════════════════════════════════════════════════════
# 2. WEIGHTED MATCHING (Skill'lere ağırlık ver)
# ═══════════════════════════════════════════════════════════

# Skill kategori ağırlıkları (isteğe göre ayarla)
SKILL_WEIGHTS = {
    "programming_language": 1.0,    # Python, Java, C++
    "framework":           0.8,     # React, Django, Spring
    "database":            0.7,     # PostgreSQL, MongoDB
    "tool":                0.5,     # Git, Docker, Jira
    "soft_skill":          0.3,     # İletişim, Takım çalışması
    "default":             0.6,
}


def weighted_match_score(
    user_skills: List[str],
    job_skills: List[str],
    skill_categories: Dict[str, str] = None,
) -> Dict:
    """
    Ağırlıklı eşleştirme skoru.
    
    Her skill'in bir kategorisi ve ağırlığı var.
    "Python bilmek" (programming_language, ağırlık=1.0) 
    "Git bilmek"ten (tool, ağırlık=0.5) daha değerli.
    
    Args:
        user_skills: Kullanıcının skill'leri
        job_skills: İlanın istediği skill'ler
        skill_categories: Her skill'in kategorisi {"python": "programming_language", ...}
    
    Returns:
        Dict with score, matched_skills, missing_skills, details
    """
    if not job_skills:
        return {"score": 0.0, "matched": [], "missing": [], "details": "No job skills"}

    if skill_categories is None:
        skill_categories = {}

    user_set = {s.lower().strip() for s in user_skills}
    job_set = {s.lower().strip() for s in job_skills}

    matched = user_set & job_set
    missing = job_set - user_set

    # Ağırlıklı skor hesapla
    total_weight = 0.0
    matched_weight = 0.0

    for skill in job_set:
        category = skill_categories.get(skill, "default")
        weight = SKILL_WEIGHTS.get(category, SKILL_WEIGHTS["default"])
        total_weight += weight
        if skill in matched:
            matched_weight += weight

    score = matched_weight / total_weight if total_weight > 0 else 0.0

    return {
        "score": round(score, 3),
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "coverage_pct": round(len(matched) / len(job_set) * 100, 1),
        "total_required": len(job_set),
        "total_matched": len(matched),
    }


# ═══════════════════════════════════════════════════════════
# 3. TF-IDF MATCHING (İleri seviye)
# ═══════════════════════════════════════════════════════════

def tfidf_similarity(user_text: str, job_texts: List[str]) -> List[float]:
    """
    TF-IDF + Cosine Similarity ile metin tabanlı eşleştirme.
    
    Skill listesi yerine serbest metinleri karşılaştırır.
    Örn: Kullanıcının CV özeti vs iş ilanı açıklamaları.
    
    NOT: Bu fonksiyon scikit-learn gerektirir.
    Eğer yüklü değilse: pip install scikit-learn
    
    Args:
        user_text: Kullanıcının profil/CV metni
        job_texts: İş ilanlarının açıklama metinleri
    
    Returns:
        Her ilan için benzerlik skoru (0.0-1.0)
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        print("scikit-learn yüklü değil. pip install scikit-learn")
        return [0.0] * len(job_texts)

    if not user_text or not job_texts:
        return [0.0] * len(job_texts)

    # Tüm metinleri birleştir (ilk eleman kullanıcı)
    all_texts = [user_text] + job_texts

    # TF-IDF vektörleri oluştur
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=1000,
        ngram_range=(1, 2),  # Tek kelime + iki kelimelik gruplar
    )
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Kullanıcı vektörü vs tüm ilan vektörleri
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

    return similarities[0].tolist()


# ═══════════════════════════════════════════════════════════
# 4. BİRLEŞİK SKOR (Hybrid Score)
# ═══════════════════════════════════════════════════════════

def calculate_match_score(
    user_skills: List[str],
    job_skills: List[str],
    user_text: str = "",
    job_text: str = "",
    skill_categories: Dict[str, str] = None,
) -> Dict:
    """
    TÜM yöntemleri birleştiren ana skor fonksiyonu.
    
    Formül:
        final_score = 0.4 * weighted_skill_score 
                    + 0.3 * coverage_score
                    + 0.2 * tfidf_score (metin varsa)
                    + 0.1 * overlap_score

    Bu fonksiyon LLM KULLANMAZ. Tamamen deterministik.
    Aynı input → her zaman aynı output.
    
    Returns:
        Dict with final_score, breakdown, matched/missing skills
    """
    user_set = {s.lower().strip() for s in user_skills}
    job_set = {s.lower().strip() for s in job_skills}

    # 1. Weighted match
    weighted = weighted_match_score(user_skills, job_skills, skill_categories)

    # 2. Coverage
    coverage = skill_coverage(user_set, job_set)

    # 3. Overlap
    overlap = overlap_coefficient(user_set, job_set)

    # 4. TF-IDF (only if text available)
    tfidf_score = 0.0
    if user_text and job_text:
        scores = tfidf_similarity(user_text, [job_text])
        tfidf_score = scores[0] if scores else 0.0

    # Birleşik skor
    if user_text and job_text:
        final = (
            0.4 * weighted["score"]
            + 0.3 * coverage
            + 0.2 * tfidf_score
            + 0.1 * overlap
        )
    else:
        # Metin yoksa sadece skill-based
        final = (
            0.5 * weighted["score"]
            + 0.35 * coverage
            + 0.15 * overlap
        )

    return {
        "final_score": round(final, 3),
        "breakdown": {
            "weighted_skill_score": weighted["score"],
            "coverage_score": round(coverage, 3),
            "overlap_score": round(overlap, 3),
            "tfidf_score": round(tfidf_score, 3),
        },
        "matched_skills": weighted["matched_skills"],
        "missing_skills": weighted["missing_skills"],
        "coverage_pct": weighted["coverage_pct"],
        "explanation": _generate_explanation(weighted, coverage, final),
    }


def _generate_explanation(weighted: Dict, coverage: float, final: float) -> str:
    """
    Eşleştirme sonucunu AÇIKLANABILIR şekilde özetle.
    LLM'den farklı olarak bu açıklama DETERMİNİSTİK — her seferinde aynı.
    """
    matched_count = weighted["total_matched"]
    required_count = weighted["total_required"]
    pct = weighted["coverage_pct"]

    if final >= 0.7:
        level = "Güçlü eşleşme"
    elif final >= 0.4:
        level = "Orta eşleşme"
    else:
        level = "Düşük eşleşme"

    parts = [
        f"{level}: {matched_count}/{required_count} gerekli skill karşılanıyor (%{pct})."
    ]

    if weighted["missing_skills"]:
        missing_str = ", ".join(weighted["missing_skills"][:5])
        parts.append(f"Eksik: {missing_str}.")

    return " ".join(parts)


# ═══════════════════════════════════════════════════════════
# 5. BATCH MATCHING (Birden fazla ilan)
# ═══════════════════════════════════════════════════════════

def rank_opportunities(
    user_skills: List[str],
    opportunities: List[Dict],
    user_text: str = "",
    top_k: int = 10,
) -> List[Dict]:
    """
    Birden fazla ilanı kullanıcıyla eşleştirip sırala.
    
    Args:
        user_skills: Kullanıcının skill'leri
        opportunities: İlan listesi, her biri {"title", "required_skills", "description", ...}
        user_text: Kullanıcının CV/profil metni
        top_k: En iyi kaç sonuç dönsün
    
    Returns:
        Skorla sıralanmış ilan listesi
    """
    scored = []

    for opp in opportunities:
        job_skills = opp.get("required_skills", [])
        job_text = opp.get("description", "")

        result = calculate_match_score(
            user_skills=user_skills,
            job_skills=job_skills,
            user_text=user_text,
            job_text=job_text,
        )

        scored.append({
            **opp,
            "match_score": result["final_score"],
            "match_breakdown": result["breakdown"],
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "match_explanation": result["explanation"],
        })

    # En yüksek skora göre sırala
    scored.sort(key=lambda x: x["match_score"], reverse=True)

    return scored[:top_k]
