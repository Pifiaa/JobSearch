import json
import math
import time
import requests
from bs4 import BeautifulSoup
from core.logger import log

BASE_URL        = "https://www.buscojobs.com.co"
SEARCH_URL_P1   = "{base}/ofertas/{query}_?fechainicio=7"
SEARCH_URL_PAGE = "{base}/ofertas/{query}_/{page}?fechainicio=7"
HEADERS         = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
}
PER_PAGE    = 15
RATE_LIMIT  = 3.0
QUERY_PAUSE = 60
MAX_PAGES   = 15


def fetch_all(base_url: str, queries: list[str]) -> list[dict]:
    seen    = set()
    results = []
    for i, query in enumerate(queries):
        if i > 0:
            log(f"[buscojobs] pausa entre queries ({QUERY_PAUSE}s)")
            time.sleep(QUERY_PAUSE)
        batch = _fetch_query(base_url, query, seen)
        results.extend(batch)
    return results


def _fetch_query(base_url: str, query: str, seen: set) -> list[dict]:
    results = []
    log(f"[buscojobs] query={query} iniciando")

    first_page = _fetch_page(base_url, query, 1)
    if not first_page:
        log(f"[buscojobs] query={query} sin resultados")
        return []

    count       = first_page["count"]
    total_pages = min(math.ceil(count / PER_PAGE), MAX_PAGES)
    log(f"[buscojobs] query={query} total={count} páginas={total_pages}")

    for oferta in first_page["ofertas"]:
        ext_id = str(oferta["IdOferta"])
        if ext_id not in seen:
            seen.add(ext_id)
            results.append(_parse_oferta(oferta))

    for page in range(2, total_pages + 1):
        time.sleep(RATE_LIMIT)
        data = _fetch_page(base_url, query, page)
        if not data:
            break
        nuevas = 0
        for oferta in data["ofertas"]:
            ext_id = str(oferta["IdOferta"])
            if ext_id not in seen:
                seen.add(ext_id)
                results.append(_parse_oferta(oferta))
                nuevas += 1
        log(f"[buscojobs] query={query} page={page}/{total_pages} nuevas={nuevas} acumulado={len(results)}")

    log(f"[buscojobs] query={query} FINALIZADA total={len(results)}")
    return results


def _fetch_page(base_url: str, query: str, page: int) -> dict | None:
    if page == 1:
        url = SEARCH_URL_P1.format(base=base_url, query=query)
    else:
        url = SEARCH_URL_PAGE.format(base=base_url, query=query, page=page)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            log(f"[buscojobs] HTTP {r.status_code} query={query} page={page}")
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            log(f"[buscojobs] __NEXT_DATA__ no encontrado query={query} page={page}")
            return None
        data = json.loads(script.text)
        return data["props"]["pageProps"]["resultadosIniciales"]
    except Exception as e:
        log(f"[buscojobs] Error query={query} page={page}: {e}")
        return None


def _parse_oferta(o: dict) -> dict:
    ciudad      = o.get("Ciudad") or {}
    depto       = o.get("Departamento") or {}
    teletrabajo = o.get("PermiteTeletrabajo", 0)
    id_oferta   = o["IdOferta"]

    return {
        "external_id":      str(id_oferta),
        "title":            o.get("CargoVacante", ""),
        "company":          o.get("NombreEmpresa", "") if not o.get("Confidencial") else "",
        "city_raw":         ciudad.get("Nombre", ""),
        "department_raw":   depto.get("Nombre", ""),
        "modality_raw":     "remote" if teletrabajo else "onsite",
        "description":      o.get("Descripcion", "") or "",
        "salary_range":     "",
        "published_at_raw": o.get("FechaInicio", ""),
        "url":              f"{BASE_URL}/{_slugify(o.get('CargoVacante', ''))}-en-{_slugify(ciudad.get('Nombre', ''))}-ID-{id_oferta}",
    }

def _slugify(text: str) -> str:
    import unicodedata
    import re
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def fetch_detail(url: str) -> dict:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        if r.status_code != 200:
            return {}
        soup = BeautifulSoup(r.text, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            return {}
        data = json.loads(script.text)
        pp   = data["props"]["pageProps"]
        oferta = pp.get("oferta")
        if not oferta:
            return {}
        return {
            "description": oferta.get("Descripcion") or None,
            "url":         oferta.get("UrlOferta") or url,
        }
    except Exception as e:
        log(f"[buscojobs] Error fetch_detail {url}: {e}")
        return {}