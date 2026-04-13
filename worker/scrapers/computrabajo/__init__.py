from base_scraper import BaseScraper
from scrapers.computrabajo.extractor import fetch_page
from scrapers.computrabajo.normalizer import normalize
from parsers.text import normalize_text


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