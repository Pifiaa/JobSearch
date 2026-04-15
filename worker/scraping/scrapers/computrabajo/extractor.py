import time
from core.logger import log
from scraping.parsers.text import is_blacklisted, normalize_text
from core.http_client import get, parse_html
from concurrent.futures import ThreadPoolExecutor, as_completed

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
DETAIL_WAIT = 0.5
DETAIL_WORKERS = 2
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "es-CO,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}

def fetch_page(base_url: str, query: str, page: int, normalized_blacklist: list[str]) -> list[dict]:
    url = f"{base_url}/trabajo-de-{query}?pubdate=15&p={page}"
    response = get(url, HEADERS)
    if response is None:
        return []
    return _parse_page(base_url, response.text, normalized_blacklist)

def _parse_page(base_url: str, html: str, normalized_blacklist: list[str]) -> list[dict]:
    soup = parse_html(html)
    vacancies = []
    for article in soup.select("article.box_offer"):
        external_id = article.get("data-id", "")
        vacancy_url = _parse_url(base_url, article)
        if not external_id or not vacancy_url:
            continue
        company_tag = article.select_one("a[offer-grid-article-company-url]")
        company = company_tag.get_text(strip=True) if company_tag else ""
        if company and is_blacklisted(company, normalized_blacklist):
            log(f"[computrabajo] Descartando empresa blacklisteada: {company}")
            continue
        title_tag = article.select_one("a.js-o-link")
        city_tag = article.select_one("p.fs16.fc_base.mt5 span.mr10")
        salary_tag = article.select_one("div.fs13.mt15 span.dIB")
        published_tag = article.select_one("p.fs13.fc_aux.mt15")
        vacancies.append({
            "external_id": external_id,
            "url": vacancy_url,
            "title": title_tag.get_text(strip=True) if title_tag else "",
            "company": company,
            "city_raw": city_tag.get_text(strip=True) if city_tag else "",
            "salary_range": salary_tag.get_text(strip=True) if salary_tag else "",
            "published_at_raw": published_tag.get_text(strip=True) if published_tag else "",
            "description": None,
            "modality_raw": "",
        })
    return vacancies

def fetch_details_parallel(vacancies: list[dict]) -> list[dict]:
    def enrich(vacancy: dict) -> dict:
        time.sleep(DETAIL_WAIT)
        description, modality_raw = fetch_detail(vacancy["url"])
        return {**vacancy, "description": description, "modality_raw": modality_raw}

    with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as executor:
        return list(executor.map(enrich, vacancies))

def fetch_detail(url: str) -> tuple[str, str]:
    response = get(url, HEADERS)
    if response is None:
        return "", ""
    soup = parse_html(response.text)
    description = soup.select_one("p.mbB")
    modality = soup.select_one("span.tag.base.mb10")
    return (
        " ".join(description.get_text().split()) if description else "",
        modality.get_text(strip=True) if modality else "",
    )

def _parse_url(base_url: str, article) -> str:
    tag = article.select_one("a.js-o-link")
    if not tag:
        return ""
    href = tag.get("href", "").strip()
    if not href:
        return ""
    return href if href.startswith("http") else f"{base_url}{href}"