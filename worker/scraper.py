import argparse
import json
import sys
from scraping.mocks import MOCK_SOURCES
from scraping.registry import Registry
from scraping.runner import Runner
from scraping.scrapers.computrabajo import ComputrabajoScraper
from scraping.scrapers.ticjob import TicjobScraper
from scraping.scrapers.elempleo import ElempleoScraper
from scraping.scrapers.getonboard import GetonboardScraper
from scraping.scrapers.buscojobs import BuscojobsScraper
from scraping.scrapers.magneto import MagnetoScraper

registry = Registry()
registry.register("computrabajo", ComputrabajoScraper)
registry.register("ticjob", TicjobScraper)
registry.register("elempleo", ElempleoScraper)
registry.register("getonboard", GetonboardScraper)
registry.register("buscojobs", BuscojobsScraper)
registry.register("magneto", MagnetoScraper)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--url", required=False)
    parser.add_argument("--config", required=False)
    parser.add_argument("--mock", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    scraper_class = registry.get(args.source)
    if not scraper_class:
        print(json.dumps({"error": f"Fuente desconocida: {args.source}"}))
        sys.exit(1)
    if args.mock:
        source = MOCK_SOURCES.get(args.source, {})
        url = source["url"]
        config = source["headers"]
    else:
        if not args.url or not args.config:
            print(json.dumps({"error": "Se requieren --url y --config"}))
            sys.exit(1)
        url = args.url
        config = json.loads(args.config)
    scraper = scraper_class(url, config)
    Runner(scraper).run()