import re
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus, urljoin

from core.http_client import get, parse_html
from core.logger import log

BASE_URL = "https://agenciapublicadeempleo.sena.edu.co"
SEARCH_PATH = "/spe-web/spe/public/buscadorVacante?solicitudId={query}"
DETAIL_WORKERS = 2
DETAIL_WAIT = 0.5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "es-CO,es;q=0.9",
}


def fetch_page(base_url: str, query: str, page: int) -> list[dict]:
    if page > 1:
        return []

    url = f"{base_url}{SEARCH_PATH.format(query=quote_plus(query))}"
    response = get(url, HEADERS)
    if response is None:
        return []

    return _parse_listing(base_url, response.text)


def fetch_details_parallel(vacancies: list[dict]) -> list[dict]:
    def enrich(vacancy: dict) -> dict:
        time.sleep(DETAIL_WAIT)
        detail = fetch_detail(vacancy["url"])
        return {**vacancy, **detail}

    with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as executor:
        return list(executor.map(enrich, vacancies))


def fetch_detail(url: str) -> dict:
    response = get(url, HEADERS)
    if response is None:
        return {}

    soup = parse_html(response.text)
    text = " ".join(soup.get_text(" ", strip=True).split())

    description = _extract_between(
        text,
        "Funciones o actividades del contrato",
        ["Habilidades", "Competencias", "Meses de experiencia"],
    )
    skills = _extract_between(text, "Habilidades", ["Competencias", "Meses de experiencia"])
    schedule = _extract_between(
        text,
        "Jornada de trabajo",
        ["Horario", "¿Es exploración", "Lugar de ejecución"],
    )

    parts = [description, skills]
    return {
        "description": " ".join(part for part in parts if part).strip(),
        "schedule_raw": schedule,
    }


def _parse_listing(base_url: str, html: str) -> list[dict]:
    soup = parse_html(html)
    vacancies = []

    table = soup.find("table")
    if not table:
        return vacancies

    rows = table.find_all("tr")
    for row in rows:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if len(cells) < 16:
            continue

        external_id = cells[1].strip()
        if not re.fullmatch(r"\d{6,8}", external_id):
            continue

        detail_link = row.find("a", href=lambda href: href and external_id in href)
        href = detail_link.get("href", "") if detail_link else ""
        detail_url = urljoin(base_url, href.split(";jsessionid=")[0]) if href else ""

        vacancies.append({
            "external_id": external_id,
            "title": cells[2],
            "department": cells[3],
            "city": cells[4],
            "vacancies_count": cells[5],
            "salary_range": cells[6],
            "telework_raw": cells[7],
            "schedule_raw": cells[8],
            "contract_type": cells[9],
            "published_at_raw": cells[10],
            "area": cells[11],
            "occupational_area": cells[12],
            "experience_months": cells[14],
            "url": detail_url,
            "description": None,
        })

    return vacancies


def _extract_between(text: str, start: str, end_markers: list[str]) -> str:
    start_index = text.find(start)
    if start_index == -1:
        return ""

    content_start = start_index + len(start)
    content_end = len(text)
    for marker in end_markers:
        marker_index = text.find(marker, content_start)
        if marker_index != -1:
            content_end = min(content_end, marker_index)

    return text[content_start:content_end].strip(' "')
