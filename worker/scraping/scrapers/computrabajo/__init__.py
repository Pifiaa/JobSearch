from scraping.base_scraper import BaseScraper
from scraping.scrapers.computrabajo.extractor import fetch_page, fetch_details_parallel
from scraping.scrapers.computrabajo.normalizer import normalize
from scraping.parsers.text import normalize_text
from core.logger import log

class ComputrabajoScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "computrabajo"

    def fetch_page(self, query: str, page: int) -> list[dict]:
        blacklist = self.config.get("blacklist", [])
        normalized_blacklist = [normalize_text(entry) for entry in blacklist]
        return fetch_page(self.base_url, query, page, normalized_blacklist)

    def parse(self, raw: list[dict]) -> list[dict]:
        blacklist = self.config.get("blacklist", [])
        return [n for v in raw if (n := normalize(v, blacklist)) is not None]

    def run(self) -> None:
        import time
        seen = set()
        raw = []
        for query in self.queries:
            raw.extend(self._fetch_with_dedup(query, seen))

        log(f"[computrabajo] Iniciando fetch_detail paralelo para {len(raw)} vacantes")
        start = time.time()
        enriched = fetch_details_parallel(raw)
        elapsed = time.time() - start
        log(f"[computrabajo] fetch_detail completado en {elapsed:.1f}s")

        vacancies = self.parse(enriched)
        self.output(vacancies)