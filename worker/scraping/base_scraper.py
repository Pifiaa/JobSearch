import json
import time
from abc import ABC, abstractmethod
from core.logger import log
from ranking.cv_reader import read_cv_text
from ranking.keyword_extractor import extract_keywords
from ranking.scorer import score_vacancy
from ranking.semantic_scorer import score_semantic


class BaseScraper(ABC):
    def __init__(self, base_url: str, config: dict):
        self.base_url = base_url
        self.config = config
        self.queries = config.get("queries", [])
        cv_text = read_cv_text()
        self.cv_keywords = extract_keywords(cv_text)
        self.cv_text = cv_text

    @abstractmethod
    def fetch_page(self, query: str, page: int) -> list[dict]:
        pass

    @abstractmethod
    def parse(self, raw: list[dict]) -> list[dict]:
        pass

    def run(self) -> None:
        seen = set()
        vacancies = []
        for query in self.queries:
            raw = self._fetch_with_dedup(query, seen)
            vacancies.extend(self.parse(raw))
        self.output(vacancies)

    def _fetch_with_dedup(self, query: str, seen: set) -> list[dict]:
        results = []
        page = 1
        start = time.time()
        log(f"[{self.source_name}] query={query} iniciando")
        while True:
            log(f"[{self.source_name}] query={query} page={page} acumulado={len(results)}")
            batch = self.fetch_page(query, page)
            if not batch:
                log(f"[{self.source_name}] query={query} sin más resultados en page={page}")
                break
            nuevas = 0
            for v in batch:
                if v["external_id"] in seen:
                    continue
                desc_hash = v.get("description_hash")
                if desc_hash and desc_hash in seen:
                    log(f"[{self.source_name}] Descartando descripción duplicada: {v['external_id']}")
                    continue
                seen.add(v["external_id"])
                if desc_hash:
                    seen.add(desc_hash)
                results.append(v)
                nuevas += 1
            elapsed = time.time() - start
            log(f"[{self.source_name}] query={query} page={page} nuevas={nuevas} acumulado={len(results)} tiempo={elapsed:.1f}s")
            page += 1
        elapsed = time.time() - start
        log(f"[{self.source_name}] query={query} FINALIZADA total={len(results)} tiempo={elapsed:.1f}s")
        return results

    def output(self, vacancies: list[dict]) -> None:
        ranked = []
        for vacancy in vacancies:
            description = vacancy.get("description") or ""
            keyword_result = score_vacancy(self.cv_keywords, description)
            semantic_score = score_semantic(self.cv_text, description)
            ranked.append({
                **vacancy,
                **keyword_result,
                "cv_score_semantic": semantic_score,
            })
        print(json.dumps({
            "source": self.source_name,
            "total": len(ranked),
            "vacancies": ranked,
        }, ensure_ascii=False))

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass