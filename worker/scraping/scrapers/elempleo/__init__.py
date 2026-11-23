import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraping.base_scraper import BaseScraper
from scraping.scrapers.elempleo.extractor import fetch_page, fetch_detail
from scraping.scrapers.elempleo.normalizer import normalize
from core.logger import log

DETAIL_WORKERS   = 5
DETAIL_WAIT      = 0.5
DETAIL_TIME_BUDGET = 900  # segundos máx. para la fase de detalle; si se excede, se corta y se guarda lo ya obtenido

class ElempleoScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "elempleo"

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

        log(f"[elempleo] Enriqueciendo {len(raw)} vacantes con detalle paralelo")
        start = time.time()
        enriched = self._fetch_details_parallel(raw)
        elapsed = time.time() - start
        log(f"[elempleo] fetch_detail completado en {elapsed:.1f}s")

        vacancies = self.parse(enriched)
        self.output(vacancies)

    def _fetch_details_parallel(self, raw: list[dict]) -> list[dict]:
        results = []
        start = time.time()
        budget_exceeded = False
        with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as executor:
            futures = {executor.submit(fetch_detail, self.base_url, v["url"]): v for v in raw}
            for future in as_completed(futures):
                vacancy = futures[future]
                try:
                    description = future.result()
                    vacancy["description"] = description
                except Exception:
                    vacancy["description"] = None
                results.append(vacancy)

                if not budget_exceeded and (time.time() - start) > DETAIL_TIME_BUDGET:
                    budget_exceeded = True
                    log(f"[elempleo] Presupuesto de tiempo excedido ({DETAIL_TIME_BUDGET}s); "
                        f"cancelando futuros pendientes, se guardan {len(results)}/{len(raw)} vacantes enriquecidas.")
                    for pending in futures:
                        pending.cancel()

                time.sleep(DETAIL_WAIT)
        return results