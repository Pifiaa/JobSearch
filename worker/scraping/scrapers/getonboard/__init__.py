from scraping.base_scraper import BaseScraper
from scraping.scrapers.getonboard.extractor import fetch_all
from scraping.scrapers.getonboard.normalizer import normalize
from core.logger import log


class GetonboardScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "getonboard"

    def fetch_page(self, query: str, page: int) -> list[dict]:
        # No usado — run() hace fetch directo
        return []

    def parse(self, raw: list[dict]) -> list[dict]:
        blacklist = self.config.get("blacklist", [])
        return [n for v in raw if (n := normalize(v, blacklist)) is not None]

    def run(self) -> None:
        queries = self.config.get("queries", [])
        log(f"[getonboard] iniciando con {len(queries)} queries")
        raw = fetch_all(queries)
        log(f"[getonboard] total raw: {len(raw)}")
        vacancies = self.parse(raw)
        self.output(vacancies)