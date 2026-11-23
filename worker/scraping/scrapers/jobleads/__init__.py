from core.logger import log
from scraping.base_scraper import BaseScraper
from scraping.scrapers.jobleads.extractor import fetch_page
from scraping.scrapers.jobleads.normalizer import normalize


class JobleadsScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "jobleads"

    def fetch_page(self, query: str, page: int) -> list[dict]:
        return fetch_page(self.base_url, query, page)

    def parse(self, raw: list[dict]) -> list[dict]:
        blacklist = self.config.get("blacklist", [])
        return [n for v in raw if (n := normalize(v, blacklist)) is not None]

    def run(self) -> None:
        # El fetch de detalle quedó bloqueado por Cloudflare Bot Management
        # (HTTP 403 incluso con sesión + Referer correctos) — ya no se
        # llama. El listado trae empresa, ciudad, modalidad y salario
        # directamente en cada tarjeta (ver extractor._parse_listing), así
        # que no hace falta la segunda petición para eso. Solo se pierde la
        # descripción completa, y base_scraper.output() ya usa el título
        # como respaldo para el scoring en ese caso.
        seen = set()
        raw = []
        for query in self.queries:
            raw.extend(self._fetch_with_dedup(query, seen))

        log(f"[jobleads] {len(raw)} vacantes extraídas del listado (sin fetch de detalle, bloqueado por Cloudflare)")

        vacancies = self.parse(raw)
        self.output(vacancies)
