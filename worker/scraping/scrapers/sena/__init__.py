import time

from core.logger import log
from scraping.base_scraper import BaseScraper
from scraping.scrapers.sena.extractor import fetch_details_parallel, fetch_page
from scraping.scrapers.sena.normalizer import normalize


class SenaScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "sena"

    def fetch_page(self, query: str, page: int) -> list[dict]:
        return fetch_page(self.base_url, query, page)

    def parse(self, raw: list[dict]) -> list[dict]:
        blacklist = self.config.get("blacklist", [])
        return [n for v in raw if (n := normalize(v, blacklist)) is not None]

    def run(self) -> None:
        seen = set()
        raw = []
        for query in self.queries:
            raw.extend(self._fetch_with_dedup(query, seen))

        log(f"[sena] Iniciando fetch_detail paralelo para {len(raw)} vacantes")
        start = time.time()
        enriched = fetch_details_parallel(raw)
        elapsed = time.time() - start
        log(f"[sena] fetch_detail completado en {elapsed:.1f}s")

        vacancies = self.parse(enriched)
        self.output(vacancies)
