from scraping.base_scraper import BaseScraper


class Registry:

    def __init__(self):
        self._scrapers: dict[str, type[BaseScraper]] = {}

    def register(self, name: str, scraper_class: type[BaseScraper]) -> None:
        self._scrapers[name] = scraper_class

    def get(self, name: str) -> type[BaseScraper] | None:
        return self._scrapers.get(name)

    def all(self) -> dict[str, type[BaseScraper]]:
        return self._scrapers