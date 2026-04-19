import hashlib
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from core.http_client import parse_html
from core.logger import log

BASE_URL        = "https://www.magneto365.com"
SEARCH_PATH     = "/co/trabajos/buscar/{query}/ultimos-15-dias?paginator[page]={page}"
HEADERS         = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.8",
}
RATE_LIMIT      = 2.0
MAX_PAGES       = 10
DETAIL_WORKERS  = 3
DETAIL_WAIT     = 0.5
BLACKLIST_COMPANIES = ["bairesdev"]


def fetch_page(base_url: str, query: str, page: int) -> list[dict]:
    if page > MAX_PAGES:
        return []
    url = base_url + SEARCH_PATH.format(query=query, page=page)
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 404:
            return []
        if response.status_code != 200:
            log(f"[magneto] HTTP {response.status_code} en page={page}")
            return []
        time.sleep(RATE_LIMIT)
        return _parse_listing(response.text)
    except Exception as e:
        log(f"[magneto] Error fetch_page page={page}: {e}")
        return []


def fetch_detail(url: str) -> str | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            return None
        soup = parse_html(response.text)
        block = soup.find("div", class_=lambda c: c and "description" in c.lower())
        if not block:
            return None
        return " ".join(block.get_text().split())
    except Exception as e:
        log(f"[magneto] Error fetch_detail {url}: {e}")
        return None


def fetch_details_parallel(raw: list[dict]) -> list[dict]:
    results = []
    with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as executor:
        futures = {executor.submit(fetch_detail, v["url"]): v for v in raw}
        for future in as_completed(futures):
            vacancy = futures[future]
            try:
                vacancy["description"] = future.result()
            except Exception:
                vacancy["description"] = None
            results.append(vacancy)
            time.sleep(DETAIL_WAIT)
    return results


def _parse_listing(html: str) -> list[dict]:
    soup = parse_html(html)
    vacancies = []

    links = soup.find_all("a", href=lambda h: h and "/co/empleos/" in h)
    seen_urls = set()

    for link in links:
        url = link.get("href", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        # Subir al article contenedor
        article = link.find_parent("article")
        if not article:
            continue

        title = link.get("title") or link.get_text(strip=True)

        # h3: "Empresa | Tipo contrato"
        h3 = article.find("h3")
        company, contract_type = "", ""
        if h3:
            parts = h3.get_text(strip=True).split("|")
            company = parts[0].strip() if parts else ""
            contract_type = parts[1].strip() if len(parts) > 1 else ""

        # párrafos: salario y ciudad
        paragraphs = article.find_all("p")
        salary_raw = paragraphs[0].get_text(strip=True) if len(paragraphs) > 0 else ""
        city_raw   = paragraphs[1].get_text(strip=True) if len(paragraphs) > 1 else ""

        # external_id desde la URL: último segmento numérico
        slug = url.rstrip("/").split("/")[-1]
        parts = slug.split("-")
        external_id = parts[-1] if parts and parts[-1].isdigit() else slug

        if any(bl in company.lower() for bl in BLACKLIST_COMPANIES):
            continue

        vacancies.append({
            "external_id":   external_id,
            "url":           url,
            "title":         title,
            "company":       company,
            "contract_type": contract_type,
            "salary_raw":    salary_raw,
            "city_raw":      city_raw,
            "description":   None,
        })

    return vacancies