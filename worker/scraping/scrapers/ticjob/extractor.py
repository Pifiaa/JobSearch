import requests
from requests.cookies import RequestsCookieJar
from core.http_client import parse_html
from core.logger import log

SEARCH_URL = "{base_url}/es/search"
AJAX_URL = "{base_url}/es/ajax/SearchResults"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0"
HEADERS = {
    "User-Agent": USER_AGENT,
}


def init_session(base_url: str) -> RequestsCookieJar:
    session = requests.Session()
    session.get(SEARCH_URL.format(base_url=base_url), headers=HEADERS, timeout=30)
    return session.cookies


def fetch_page(base_url: str, page: int, cookies: RequestsCookieJar) -> list[dict]:
    data = {
        "searchPage": "true",
        "displayExtracts": "false",
        "noResultTeaser": "true",
        "anchorAsUrl": "true",
        "displayRSSLink": "true",
        "keywords": "",
        "keywordOptions": "OR",
        "locations": "",
        "page": str(page),
    }
    headers = {
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": SEARCH_URL.format(base_url=base_url),
        "Accept": "text/html, */*; q=0.01",
    }
    response = requests.post(
        AJAX_URL.format(base_url=base_url),
        data=data,
        headers=headers,
        cookies=cookies,
        timeout=30,
    )
    if response.status_code != 200:
        return []
    return _parse_page(base_url, response.text)


def _parse_page(base_url: str, html: str) -> list[dict]:
    soup = parse_html(html)
    vacancies = []

    for card in soup.select("div.job-card"):
        raw_url = card.get("data-url", "")
        external_id = _extract_id(raw_url)
        vacancy_url = _normalize_url(base_url, raw_url)

        if not external_id or not vacancy_url:
            continue

        if card.find("span", class_="remoteJobLabel"):
            modality_raw = "remote"
        elif card.find("span", class_="hybridJobLabel"):
            modality_raw = "hybrid"
        else:
            modality_raw = "onsite"

        vacancies.append({
            "external_id": external_id,
            "url": vacancy_url,
            "title": card.select_one("h2.job-title").get_text(strip=True) if card.select_one("h2.job-title") else "",
            "company": card.select_one("div.job-card-label-header h3").get_text(strip=True) if card.select_one("div.job-card-label-header h3") else "",
            "location_raw": card.select_one("div.job-card-label.location-field p").get_text(strip=True) if card.select_one("div.job-card-label.location-field p") else "",
            "salary_range": card.select_one("div.job-card-label.salary-field p").get_text(strip=True) if card.select_one("div.job-card-label.salary-field p") else "",
            "published_at_raw": card.select_one("div.job-card-label.date-field p").get_text(strip=True) if card.select_one("div.job-card-label.date-field p") else "",
            "description": " ".join(card.select_one("div.job-description p").get_text().split()) if card.select_one("div.job-description p") else "",
            "modality_raw": modality_raw,
        })

    return vacancies


def _extract_id(raw_url: str) -> str:
    parts = raw_url.rstrip("/").split("/")
    return parts[-1] if parts else ""


def _normalize_url(base_url: str, raw_url: str) -> str:
    if not raw_url:
        return ""
    if raw_url.startswith("http"):
        return raw_url
    return f"{base_url}{raw_url}"