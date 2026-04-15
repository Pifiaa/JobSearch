import json
import sys
from scraping.base_scraper import BaseScraper


class Runner:

    def __init__(self, scraper: BaseScraper):
        self.scraper = scraper

    def run(self) -> None:
        try:
            self.scraper.run()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.exit(1)