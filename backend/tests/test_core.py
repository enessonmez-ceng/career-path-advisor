"""
Test Suite — Career Path Advisor
================================

📚 KAYNAKLAR (Bunları oku/izle):
─────────────────────────────────
1. pytest resmi dokümantasyon:
   https://docs.pytest.org/en/stable/
   → pytest'in temel kullanımı, fixture'lar, parametrize.

2. pytest fixtures:
   https://docs.pytest.org/en/stable/how-to/fixtures.html
   → Test verisi hazırlama. @pytest.fixture decorator'ü.

3. Mocking (unittest.mock):
   https://docs.python.org/3/library/unittest.mock.html
   → API çağrılarını taklit etme. LLM/Supabase çağrılarını mock'lamak için.

4. YouTube - "pytest Tutorial":
   https://www.youtube.com/results?search_query=pytest+tutorial+beginner
   → Görsel öğrenme için.

5. Test Coverage:
   https://pytest-cov.readthedocs.io/
   → pip install pytest-cov
   → pytest --cov=graph tests/ → kaç satır test ediliyor gösterir.

ÇALIŞTIRMA:
───────────
   cd backend
   pytest tests/ -v              # Tüm testleri çalıştır
   pytest tests/ -v -k "skill"   # Sadece skill testlerini çalıştır
   pytest tests/ --cov=graph     # Coverage raporu ile
"""
import pytest
import sys
import os

# Backend dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════
# 1. SKILL MATCHER TESTLERİ
# ═══════════════════════════════════════════════════════════

class TestJaccardSimilarity:
    """Jaccard benzerlik testleri"""

    def test_identical_sets(self):
        from graph.utils.skill_matcher import jaccard_similarity
        assert jaccard_similarity({"python", "java"}, {"python", "java"}) == 1.0

    def test_disjoint_sets(self):
        from graph.utils.skill_matcher import jaccard_similarity
        assert jaccard_similarity({"python"}, {"java"}) == 0.0

    def test_partial_overlap(self):
        from graph.utils.skill_matcher import jaccard_similarity
        # {python, react} ∩ {python, java} = {python} → 1/3
        result = jaccard_similarity({"python", "react"}, {"python", "java"})
        assert round(result, 2) == 0.33

    def test_empty_sets(self):
        from graph.utils.skill_matcher import jaccard_similarity
        assert jaccard_similarity(set(), {"python"}) == 0.0
        assert jaccard_similarity(set(), set()) == 0.0


class TestSkillCoverage:
    """İlan gereksinimlerinin ne kadarı karşılanıyor?"""

    def test_full_coverage(self):
        from graph.utils.skill_matcher import skill_coverage
        user = {"python", "react", "sql"}
        required = {"python", "react"}
        assert skill_coverage(user, required) == 1.0

    def test_no_coverage(self):
        from graph.utils.skill_matcher import skill_coverage
        user = {"python"}
        required = {"java", "spring"}
        assert skill_coverage(user, required) == 0.0

    def test_half_coverage(self):
        from graph.utils.skill_matcher import skill_coverage
        user = {"python", "sql"}
        required = {"python", "java", "sql", "docker"}
        assert skill_coverage(user, required) == 0.5


class TestWeightedMatchScore:
    """Ağırlıklı eşleştirme testleri"""

    def test_returns_dict(self):
        from graph.utils.skill_matcher import weighted_match_score
        result = weighted_match_score(["python"], ["python", "java"])
        assert isinstance(result, dict)
        assert "score" in result
        assert "matched_skills" in result
        assert "missing_skills" in result

    def test_all_matched(self):
        from graph.utils.skill_matcher import weighted_match_score
        result = weighted_match_score(["python", "java"], ["python", "java"])
        assert result["score"] == 1.0
        assert result["coverage_pct"] == 100.0

    def test_none_matched(self):
        from graph.utils.skill_matcher import weighted_match_score
        result = weighted_match_score(["python"], ["java", "spring"])
        assert result["score"] == 0.0
        assert len(result["missing_skills"]) == 2


class TestCalculateMatchScore:
    """Birleşik skor testleri"""

    def test_returns_all_fields(self):
        from graph.utils.skill_matcher import calculate_match_score
        result = calculate_match_score(["python", "sql"], ["python", "java", "sql"])
        assert "final_score" in result
        assert "breakdown" in result
        assert "explanation" in result
        assert 0.0 <= result["final_score"] <= 1.0

    def test_perfect_match_high_score(self):
        from graph.utils.skill_matcher import calculate_match_score
        result = calculate_match_score(
            ["python", "react", "sql"],
            ["python", "react", "sql"],
        )
        assert result["final_score"] >= 0.8

    def test_no_match_low_score(self):
        from graph.utils.skill_matcher import calculate_match_score
        result = calculate_match_score(
            ["python"],
            ["java", "spring", "kubernetes"],
        )
        assert result["final_score"] < 0.3


# ═══════════════════════════════════════════════════════════
# 2. LLM VALIDATOR TESTLERİ
# ═══════════════════════════════════════════════════════════

class TestFuzzyFindSkill:
    """Fuzzy skill matching testleri"""

    def test_exact_match(self):
        from graph.utils.llm_validator import fuzzy_find_skill
        assert fuzzy_find_skill("python") == "python"

    def test_alias_match(self):
        from graph.utils.llm_validator import fuzzy_find_skill
        assert fuzzy_find_skill("js") == "javascript"
        assert fuzzy_find_skill("ts") == "typescript"
        assert fuzzy_find_skill("k8s") == "kubernetes"

    def test_unknown_skill(self):
        from graph.utils.llm_validator import fuzzy_find_skill
        result = fuzzy_find_skill("quantumflux_programming_xyz")
        assert result is None


class TestValidateSkills:
    """LLM skill çıktı doğrulama testleri"""

    def test_valid_skills_pass(self):
        from graph.utils.llm_validator import validate_skills
        result = validate_skills(["python", "react", "sql"])
        assert len(result["validated"]) == 3
        assert len(result["rejected"]) == 0

    def test_alias_correction(self):
        from graph.utils.llm_validator import validate_skills
        result = validate_skills(["js", "ts", "py"])
        assert "javascript" in result["validated"]
        assert "typescript" in result["validated"]
        assert "python" in result["validated"]

    def test_empty_input(self):
        from graph.utils.llm_validator import validate_skills
        result = validate_skills([])
        assert result["validated"] == []
        assert result["confidence"] == 0.0

    def test_too_short_rejected(self):
        from graph.utils.llm_validator import validate_skills
        result = validate_skills(["a", "python"])
        assert len(result["rejected"]) == 1

    def test_strict_mode_rejects_unknown(self):
        from graph.utils.llm_validator import validate_skills
        result = validate_skills(["python", "unobtanium_framework"], strict=True)
        assert "python" in result["validated"]
        assert len(result["rejected"]) >= 1


# ═══════════════════════════════════════════════════════════
# 3. CACHE SERVICE TESTLERİ
# ═══════════════════════════════════════════════════════════

class TestInMemoryCache:
    """Cache mekanizması testleri"""

    def test_set_and_get(self):
        from graph.utils.cache_service import InMemoryCache
        cache = InMemoryCache(ttl=60)
        cache.set("key1", {"data": "test"})
        assert cache.get("key1") == {"data": "test"}

    def test_miss_returns_none(self):
        from graph.utils.cache_service import InMemoryCache
        cache = InMemoryCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiry(self):
        import time
        from graph.utils.cache_service import InMemoryCache
        cache = InMemoryCache(ttl=1)  # 1 saniye TTL
        cache.set("key1", "value1")
        time.sleep(1.5)
        assert cache.get("key1") is None  # Süresi dolmuş

    def test_max_size_eviction(self):
        from graph.utils.cache_service import InMemoryCache
        cache = InMemoryCache(ttl=60, max_size=2)
        cache.set("key1", "val1")
        cache.set("key2", "val2")
        cache.set("key3", "val3")  # key1 evict edilmeli
        assert cache.get("key3") == "val3"
        assert cache.get("key1") is None

    def test_stats_tracking(self):
        from graph.utils.cache_service import InMemoryCache
        cache = InMemoryCache()
        cache.set("k1", "v1")
        cache.get("k1")  # hit
        cache.get("k2")  # miss
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_clear(self):
        from graph.utils.cache_service import InMemoryCache
        cache = InMemoryCache()
        cache.set("k1", "v1")
        cache.clear()
        assert cache.get("k1") is None


class TestCacheDecorator:
    """@cached decorator testleri"""

    def test_decorator_caches_result(self):
        from graph.utils.cache_service import InMemoryCache, cached

        cache = InMemoryCache(ttl=60)
        call_count = 0

        @cached(cache)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)  # Cache'den gelmeli

        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Sadece 1 kez çağrılmalı


# ═══════════════════════════════════════════════════════════
# 4. INTEGRATION TESTLERİ
# ═══════════════════════════════════════════════════════════

class TestRankOpportunities:
    """Toplu eşleştirme ve sıralama testi"""

    def test_ranking_order(self):
        from graph.utils.skill_matcher import rank_opportunities

        user_skills = ["python", "react", "sql"]
        opportunities = [
            {"title": "Java Developer", "required_skills": ["java", "spring"]},
            {"title": "Full Stack Dev", "required_skills": ["python", "react", "sql"]},
            {"title": "Data Analyst", "required_skills": ["python", "sql", "excel"]},
        ]

        ranked = rank_opportunities(user_skills, opportunities, top_k=3)
        # Full Stack Dev should be #1 (perfect match)
        assert ranked[0]["title"] == "Full Stack Dev"
        assert ranked[0]["match_score"] > ranked[1]["match_score"]
