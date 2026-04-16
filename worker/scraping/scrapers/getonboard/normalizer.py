import hashlib
from datetime import datetime
from core.enums import VacancyModality
from scraping.parsers.text import is_blacklisted


def normalize(raw: dict, blacklist: list[str]) -> dict | None:
    if not raw.get("title"):
        return None

    if raw.get("lang") == "en":
        return None

    company = raw.get("company", "") or ""
    if company and is_blacklisted(company, blacklist):
        return None

    return {
        "external_id":      raw["external_id"],
        "title":            raw["title"],
        "company":          company or None,
        "city":             raw.get("city_raw") or None,
        "department":       None,
        "country":          "CO",
        "modality":         _parse_modality(raw.get("modality_raw", "")).value,
        "salary_range":     raw.get("salary_range") or None,
        "description":      raw.get("description") or None,
        "description_hash": hashlib.md5(raw["description"].encode()).hexdigest() if raw.get("description") else None,
        "url":              raw["url"],
        "published_at":     _parse_date(raw.get("published_at_raw", "")),
    }


def _parse_modality(modality_raw: str) -> VacancyModality:
    match modality_raw:
        case "fully_remote":
            return VacancyModality.REMOTO_INTERNACIONAL
        case "hybrid":
            return VacancyModality.HIBRIDO
        case _:
            return VacancyModality.PRESENCIAL


def _parse_date(raw: str) -> str | None:
    if not raw:
        return None
    try:
        dt = datetime.fromtimestamp(int(raw))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None