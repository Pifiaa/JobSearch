from base_scraper import BaseScraper
from scrapers.ticjob.extractor import fetch_page, init_session
from scrapers.ticjob.normalizer import normalize


class TicjobScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "ticjob"

    def run(self) -> None:
        self._cookies = init_session(self.base_url)
        seen = set()
        raw = self._fetch_with_dedup("", seen)
        vacancies = self.parse(raw)
        self.output(vacancies)

    def fetch_page(self, query: str, page: int) -> list[dict]:
        return fetch_page(self.base_url, page, self._cookies)

    def parse(self, raw: list[dict]) -> list[dict]:
        blacklist = self.config.get("blacklist", [])
        return [n for v in raw if (n := normalize(v, blacklist)) is not None]