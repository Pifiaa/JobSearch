import time
from scraping.base_scraper import BaseScraper
from scraping.scrapers.magneto.extractor import fetch_page, fetch_details_parallel
from scraping.scrapers.magneto.normalizer import normalize
from core.logger import log


class MagnetoScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "magneto"

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

        log(f"[magneto] Enriqueciendo {len(raw)} vacantes con detalle paralelo")
        start = time.time()
        enriched = fetch_details_parallel(raw)
        elapsed = time.time() - start
        log(f"[magneto] fetch_detail completado en {elapsed:.1f}s")

        vacancies = self.parse(enriched)
        self.output(vacancies)