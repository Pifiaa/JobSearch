import re
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus, urljoin

from core.http_client import get, parse_html

SEARCH_PATH = "/search/jobs?keywords={query}&location_country=CO&minSalary=0"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.6",
}
DETAIL_WORKERS = 2
DETAIL_WAIT = 0.5
MAX_RESULTS_PER_QUERY = 30


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

    title = _extract_title(soup)
    company = _extract_after_title(text, title)
    city = _extract_location(text)
    modality_raw = _extract_modality(text)
    salary_raw = _extract_salary(text)
    published_at_raw = _extract_age(text)
    description = _extract_description(text)

    return {
        "title": title,
        "company": company,
        "city_raw": city,
        "modality_raw": modality_raw,
        "salary_range": salary_raw,
        "published_at_raw": published_at_raw,
        "description": description,
    }


def _parse_listing(base_url: str, html: str) -> list[dict]:
    soup = parse_html(html)
    vacancies = []
    seen = set()

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "/job/" not in href:
            continue

        url = urljoin(base_url, href)
        external_id = url.rstrip("/").split("/")[-1]
        if external_id in seen:
            continue
        seen.add(external_id)

        title = " ".join(link.get_text(" ", strip=True).split())
        vacancies.append({
            "external_id": external_id,
            "url": url,
            "title": title,
            "company": None,
            "city_raw": "",
            "modality_raw": "",
            "salary_range": "",
            "published_at_raw": "",
            "description": None,
        })

        if len(vacancies) >= MAX_RESULTS_PER_QUERY:
            break

    return vacancies


def _extract_title(soup) -> str:
    h1 = soup.find("h1")
    if h1:
        return " ".join(h1.get_text(" ", strip=True).split())

    if soup.title:
        return soup.title.get_text(strip=True).split("|")[0].split("-")[0].strip()

    return ""


def _extract_after_title(text: str, title: str) -> str | None:
    if not title:
        return None

    marker = f"{title} "
    index = text.find(marker)
    if index == -1:
        return None

    tail = text[index + len(marker):]
    stop_words = [
        "Colombia",
        "Bogotá",
        "Cali",
        "Medellín",
        "Barranquilla",
        "Aguachica",
        "Perímetro Urbano",
        "Distrito Capital",
        "Presencial",
        "A distancia",
        "Híbrido",
        "Solo para miembros registrados",
        "Hace ",
        "Descripción de la vacante",
        "Descripción del empleo",
        "Solicitar ahora",
        "JobLeads",
    ]
    stop_indexes = [tail.find(word) for word in stop_words if tail.find(word) != -1]
    if not stop_indexes:
        return None

    company = tail[:min(stop_indexes)].strip()
    if not company or len(company) > 120:
        return None
    return company


def _extract_location(text: str) -> str:
    match = re.search(r"Solo para miembros registrados\s+(.+?)\s+(Presencial|A distancia|Híbrido)", text)
    if match:
        return match.group(1).strip()
    return ""


def _extract_modality(text: str) -> str:
    for value in ["A distancia", "Híbrido", "Presencial"]:
        if value in text:
            return value
    return ""


def _extract_salary(text: str) -> str:
    match = re.search(r"COP\s+[0-9.]+(?:\s*-\s*[0-9.]+)?", text)
    return match.group(0).strip() if match else ""


def _extract_age(text: str) -> str:
    match = re.search(r"Hace\s+[^.]+?(?=\s+Descripción de la vacante|\s+Descripción del empleo|\s+Formación)", text)
    return match.group(0).strip() if match else ""


def _extract_description(text: str) -> str:
    start_markers = ["Descripción de la vacante", "Descripción del empleo"]
    end_markers = [
        "Trabajos similares",
        "Solicitar ahora",
        "Quiero recibir",
        "Accede sin restricciones",
        "Impulso para la búsqueda de empleo",
        "Herramientas Trabajos",
        "Empresa Sobre JobLeads",
        "Países Elija sus preferencias",
        "© JobLeads",
        "Lorem ipsum",
        "Sed ut perspiciatis",
        "At vero eos",
        "Nemo enim ipsam",
        "Tu puesto",
        "Tu perfil",
        "Servicios",
    ]

    start = -1
    start_marker_used = ""
    for marker in start_markers:
        start = text.find(marker)
        if start != -1:
            start += len(marker)
            start_marker_used = marker
            break

    if start == -1:
        return text[:3000]

    end = len(text)
    for marker in end_markers:
        marker_index = text.find(marker, start)
        if marker_index != -1:
            end = min(end, marker_index)

    description = text[start:end].strip()
    description = _trim_duplicate_employment_section(description, start_marker_used)
    return _keep_useful_sections(description)


def _trim_duplicate_employment_section(text: str, start_marker_used: str) -> str:
    if not text:
        return ""

    duplicate_markers = ["Descripción del empleo", "Descripción de la vacante"]
    for marker in duplicate_markers:
        if marker == start_marker_used:
            continue
        marker_index = text.find(marker)
        if marker_index != -1:
            return text[:marker_index].strip()

    if start_marker_used == "Descripción de la vacante":
        marker_index = text.find("Descripción del empleo")
        if marker_index != -1:
            return text[:marker_index].strip()

    return text


def _keep_useful_sections(text: str) -> str:
    if not text:
        return ""

    section_markers = [
        "Formación",
        "Responsabilidades",
        "Conocimientos",
        "Educación",
        "Habilidades",
        "Competencias",
    ]

    stop_markers = [
        "Descripción del empleo Descripción del empleo",
        "Descripción de la vacante Descripción del empleo",
        "Lorem ipsum",
        "Sed ut perspiciatis",
        "At vero eos",
        "Nemo enim ipsam",
        "Aliquam placerat",
        "Sed nec justo",
        "Suspendisse quis mauris",
        "Aenean vitae tincidunt",
        "Quisque sit amet massa",
        "Nullam facilisis odio",
        "Orci varius natoque",
        "Maecenas eu ipsum",
        "Phasellus vel egestas",
        "Etiam congue sem",
        "Vivamus semper",
        "Tu puesto",
        "Tu perfil",
        "Servicios",
        "Accede sin restricciones",
        "Impulso para la búsqueda de empleo",
        "Herramientas Trabajos",
        "Empresa Sobre JobLeads",
        "Países Elija sus preferencias",
        "© JobLeads",
    ]

    main_end = len(text)
    for marker in stop_markers:
        marker_index = text.find(marker)
        if marker_index != -1:
            main_end = min(main_end, marker_index)

    main = text[:main_end].strip()
    if not main:
        return ""

    extra_sections = []
    for marker in section_markers:
        marker_index = text.find(marker)
        if marker_index == -1 or marker_index >= main_end:
            continue

        section_end = main_end
        for next_marker in section_markers + stop_markers:
            next_index = text.find(next_marker, marker_index + len(marker))
            if next_index != -1:
                section_end = min(section_end, next_index)

        section_text = text[marker_index:section_end].strip()
        if section_text and section_text not in extra_sections:
            extra_sections.append(section_text)

    parts = [main] + [section for section in extra_sections if section not in main]
    return " ".join(parts).strip()
