import json
import time
import requests
from core.http_client import parse_html
from core.logger import log

BASE_URL     = "https://www.elempleo.com"
SEARCH_PATH  = "/co/ofertas-empleo/{query}/{page}?PublishDate=hace-2-semanas"
HEADERS      = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept":     "text/html,application/xhtml+xml,*/*;q=0.8",
}
RATE_LIMIT   = 3.0
MAX_PAGES    = 15
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
            log(f"[elempleo] HTTP {response.status_code} en page={page}")
            return []
        time.sleep(RATE_LIMIT)
        return _parse_listing(response.text)
    except Exception as e:
        log(f"[elempleo] Error fetch_page page={page}: {e}")
        return []


def fetch_detail(base_url: str, url: str) -> str | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            return None
        soup = parse_html(response.text)
        block = soup.find("div", class_="description-block")
        if not block:
            return None
        return " ".join(block.get_text().split())
    except Exception as e:
        log(f"[elempleo] Error fetch_detail {url}: {e}")
        return None


def _parse_listing(html: str) -> list[dict]:
    soup = parse_html(html)
    items = soup.find_all("div", class_="js-area-bind")
    vacancies = []
    for item in items:
        ga4 = item.get("data-ga4-offerdata", "{}")
        try:
            ga4_data = json.loads(ga4)
        except Exception:
            ga4_data = {}

        company = ga4_data.get("company", "") or ""
        if any(bl in company.lower() for bl in BLACKLIST_COMPANIES):
            continue

        raw_url  = item.get("data-url", "")
        full_url = _build_url(raw_url)
        ext_id   = _extract_id(raw_url)

        if not ext_id or not full_url:
            continue

        modality_div = item.find("div", class_="js-work-modality")
        modality_raw = ""
        if modality_div and "hide" not in modality_div.get("class", []):
            modality_raw = modality_div.get_text(strip=True).lower()

        date_span  = item.find("span", class_="js-offer-date")
        city_span  = item.find("span", class_="js-offer-city")
        salary_div = item.find("div", class_="text-blue-petrol-dark")

        vacancies.append({
            "external_id":      ext_id,
            "url":              full_url,
            "title":            ga4_data.get("title", ""),
            "company":          company,
            "city_raw":         city_span.get_text(strip=True) if city_span else "",
            "salary_range":     salary_div.get_text(strip=True) if salary_div else "",
            "published_at_raw": date_span.get_text(strip=True) if date_span else "",
            "modality_raw":     modality_raw,
            "description":      None,
        })
    return vacancies


def _build_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    if raw_url.startswith("http"):
        return raw_url
    return f"{BASE_URL}{raw_url}"


def _extract_id(raw_url: str) -> str:
    path = raw_url.split("?")[0].rstrip("/")
    parts = path.split("-")
    return parts[-1] if parts else ""