import argparse
import json
import sys
from mocks import MOCK_SOURCES
from registry import Registry
from runner import Runner
from scrapers.computrabajo import ComputrabajoScraper
from scrapers.ticjob import TicjobScraper

registry = Registry()
registry.register("computrabajo", ComputrabajoScraper)
registry.register("ticjob", TicjobScraper)

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