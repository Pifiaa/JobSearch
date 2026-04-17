from scraping.base_scraper import BaseScraper
from scraping.scrapers.buscojobs.extractor import fetch_all
from scraping.scrapers.buscojobs.normalizer import normalize
from core.logger import log


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
        log(f"[buscojobs] total raw: {len(raw)}")
        vacancies = self.parse(raw)
        self.output(vacancies)