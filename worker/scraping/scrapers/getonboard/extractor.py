import time
import requests
from bs4 import BeautifulSoup
from core.logger import log

API_URL    = "https://www.getonbrd.com/api/v0/search/jobs"
PER_PAGE   = 120
RATE_LIMIT = 1.0


def fetch_all(queries: list[str]) -> list[dict]:
    seen = set()
    results = []
    for query in queries:
        batch = _fetch_query(query, seen)
        results.extend(batch)
    return results


def _fetch_query(query: str, seen: set) -> list[dict]:
    results = []
    page = 1
    log(f"[getonboard] query={query} iniciando")
    while True:
        params = {
            "query":    query,
            "per_page": PER_PAGE,
            "page":     page,
            "expand[]": "company",
            "lang":     "es",
        }
        try:
            r = requests.get(API_URL, params=params, timeout=30)
            if r.status_code != 200:
                log(f"[getonboard] HTTP {r.status_code} query={query} page={page}")
                break
            data = r.json()
        except Exception as e:
            log(f"[getonboard] Error query={query} page={page}: {type(e).__name__}: {e}")
            break

        for job in data.get("data", []):
            ext_id = job.get("id", "")
            if ext_id in seen:
                continue
            seen.add(ext_id)
            results.append(_parse_job(job))

        meta       = data.get("meta", {})
        total_pages = meta.get("total_pages", 1)
        log(f"[getonboard] query={query} page={page}/{total_pages} acumulado={len(results)}")

        if page >= total_pages:
            break
        page += 1
        time.sleep(RATE_LIMIT)

    log(f"[getonboard] query={query} FINALIZADA total={len(results)}")
    return results


def _parse_job(job: dict) -> dict:
    attrs   = job.get("attributes", {})
    company = attrs.get("company", {}).get("data", {}).get("attributes", {})

    description_html = attrs.get("description", "") or ""
    description      = _strip_html(description_html)

    countries = attrs.get("countries", []) or []
    cities    = attrs.get("location_cities", []) or []

    min_sal = attrs.get("min_salary") or 0
    max_sal = attrs.get("max_salary") or 0
    salary  = f"{min_sal} - {max_sal}" if min_sal or max_sal else ""

    return {
        "external_id":      job.get("id", ""),
        "title":            attrs.get("title", ""),
        "company":          company.get("name", ""),
        "description":      description,
        "modality_raw":     attrs.get("remote_modality", ""),
        "countries":        countries,
        "city_raw":         cities[0] if isinstance(cities, list) and cities else "",
        "salary_range":     salary,
        "published_at_raw": str(attrs.get("published_at", "")),
        "url":              job.get("links", {}).get("public_url", ""),
    }


def _strip_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return " ".join(soup.get_text().split())