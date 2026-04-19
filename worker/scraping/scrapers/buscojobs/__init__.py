import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraping.base_scraper import BaseScraper
from scraping.scrapers.buscojobs.extractor import fetch_all, fetch_detail
from scraping.scrapers.buscojobs.normalizer import normalize
from core.logger import log

DETAIL_WORKERS = 2
DETAIL_WAIT    = 2.0


class BuscojobsScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "buscojobs"

    def fetch_page(self, query: str, page: int) -> list[dict]:
        return []

    def parse(self, raw: list[dict]) -> list[dict]:
        blacklist = self.config.get("blacklist", [])
        return [n for v in raw if (n := normalize(v, blacklist)) is not None]

    def run(self) -> None:
        queries = self.config.get("queries", [])
        log(f"[buscojobs] iniciando con {len(queries)} queries")
        raw = fetch_all(self.base_url, queries)
        log(f"[buscojobs] total raw: {len(raw)} — enriqueciendo con detalles")
        enriched = self._fetch_details_parallel(raw)
        vacancies = self.parse(enriched)
        self.output(vacancies)

    def _fetch_details_parallel(self, raw: list[dict]) -> list[dict]:
        results = []
        with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as executor:
            futures = {executor.submit(fetch_detail, v["url"]): v for v in raw}
            for future in as_completed(futures):
                vacancy = futures[future]
                try:
                    detail = future.result()
                    if detail.get("description"):
                        vacancy["description"] = detail["description"]
                    if detail.get("url"):
                        vacancy["url"] = detail["url"]
                except Exception:
                    pass
                results.append(vacancy)
                time.sleep(DETAIL_WAIT)
        return results