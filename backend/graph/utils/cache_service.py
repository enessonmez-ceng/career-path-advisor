"""
Cache Service — API Yanıt Önbelleği (Maliyet Optimizasyonu)
============================================================

📚 KAYNAKLAR (Bunları oku/izle):
─────────────────────────────────
1. Python functools.lru_cache:
   https://docs.python.org/3/library/functools.html#functools.lru_cache
   → Python'un built-in cache mekanizması. En basit yöntem.

2. Caching Strategies:
   https://aws.amazon.com/caching/best-practices/
   → Cache-aside, Write-through, TTL gibi stratejiler.

3. Redis ile caching (ileri seviye):
   https://redis.io/docs/latest/develop/
   → Distributed cache. Birden fazla sunucu varsa gerekli.

4. Hash fonksiyonları:
   https://docs.python.org/3/library/hashlib.html
   → Cache key oluşturmak için kullanılır.

5. YouTube - "API Caching Patterns":
   https://www.youtube.com/results?search_query=api+response+caching+python
   → Pratik örnekler.

AMAÇ:
─────
Aynı CV iki kez yüklenirse LLM'i tekrar çağırma!
Bu dosya:
  1. LLM yanıtlarını in-memory cache'de tutar
  2. Aynı input gelince cache'den döner (ücretsiz + anında)
  3. Cache TTL (Time To Live) ile eski verileri siler
  4. Kaç çağrı kaydedildi (cache hit/miss) loglar

Mülakatçıya: "OpenAI maliyetini caching ile %60-70 düşürdüm"
"""

import hashlib
import json
import time
from typing import Any, Optional, Dict
from functools import wraps


# ═══════════════════════════════════════════════════════════
# 1. IN-MEMORY CACHE (Basit ama etkili)
# ═══════════════════════════════════════════════════════════

class InMemoryCache:
    """
    TTL destekli in-memory cache.
    
    Avantajları:
        - Harici servis gerekmez (Redis yok)
        - Sıfır maliyet
        - Microsaniye erişim süresi
    
    Dezavantajları:
        - Sunucu yeniden başlarsa cache sıfırlanır
        - Bellek sınırlı (max_size ile kontrol)
    
    Kullanım:
        cache = InMemoryCache(ttl=3600)  # 1 saat
        cache.set("key", {"data": "value"})
        result = cache.get("key")  # → {"data": "value"}
    """

    def __init__(self, ttl: int = 3600, max_size: int = 500):
        """
        Args:
            ttl: Saniye cinsinden yaşam süresi (varsayılan: 1 saat)
            max_size: Maksimum cache girişi sayısı
        """
        self._store: Dict[str, Dict] = {}
        self._ttl = ttl
        self._max_size = max_size
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}

    def _make_key(self, *args, **kwargs) -> str:
        """Input'lardan deterministik bir cache key oluştur."""
        raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, key: str) -> Optional[Any]:
        """Cache'den değer al. Süresi dolmuşsa None döner."""
        entry = self._store.get(key)
        if entry is None:
            self._stats["misses"] += 1
            return None

        # TTL kontrolü
        if time.time() - entry["timestamp"] > self._ttl:
            del self._store[key]
            self._stats["misses"] += 1
            self._stats["evictions"] += 1
            return None

        self._stats["hits"] += 1
        return entry["value"]

    def set(self, key: str, value: Any) -> None:
        """Cache'e değer yaz."""
        # Max size kontrolü (LRU benzeri — en eski girişi sil)
        if len(self._store) >= self._max_size:
            oldest_key = min(self._store, key=lambda k: self._store[k]["timestamp"])
            del self._store[oldest_key]
            self._stats["evictions"] += 1

        self._store[key] = {
            "value": value,
            "timestamp": time.time(),
        }

    def clear(self) -> None:
        """Tüm cache'i temizle."""
        self._store.clear()

    def get_stats(self) -> Dict:
        """Cache istatistiklerini döner."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0.0

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate": round(hit_rate, 2),
            "size": len(self._store),
            "max_size": self._max_size,
            "savings_estimate": f"~${self._stats['hits'] * 0.003:.3f} saved",
        }


# ═══════════════════════════════════════════════════════════
# 2. GLOBAL CACHE INSTANCES
# ═══════════════════════════════════════════════════════════

# Her LLM görevi için ayrı cache
cv_parse_cache = InMemoryCache(ttl=7200, max_size=100)       # 2 saat
skill_extract_cache = InMemoryCache(ttl=7200, max_size=200)  # 2 saat
embedding_cache = InMemoryCache(ttl=86400, max_size=1000)    # 24 saat
opportunity_cache = InMemoryCache(ttl=3600, max_size=500)    # 1 saat


# ═══════════════════════════════════════════════════════════
# 3. CACHE DECORATOR (En kolay kullanım)
# ═══════════════════════════════════════════════════════════

def cached(cache_instance: InMemoryCache):
    """
    Herhangi bir fonksiyonu cache'le.
    
    Kullanım:
        @cached(embedding_cache)
        def generate_embedding(text: str):
            return openai.embeddings.create(...)
    
    İlk çağrı: OpenAI API çağrılır, sonuç cache'lenir
    Sonraki çağrılar: Cache'den gelir (ücretsiz + anında)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = cache_instance._make_key(func.__name__, *args, **kwargs)
            
            # Cache'de var mı?
            cached_result = cache_instance.get(key)
            if cached_result is not None:
                return cached_result
            
            # Yoksa fonksiyonu çağır ve cache'le
            result = func(*args, **kwargs)
            cache_instance.set(key, result)
            return result
        
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# 4. TOPLU İSTATİSTİK
# ═══════════════════════════════════════════════════════════

def get_all_cache_stats() -> Dict:
    """Tüm cache instance'larının istatistiklerini döner."""
    return {
        "cv_parse": cv_parse_cache.get_stats(),
        "skill_extract": skill_extract_cache.get_stats(),
        "embedding": embedding_cache.get_stats(),
        "opportunity": opportunity_cache.get_stats(),
    }
