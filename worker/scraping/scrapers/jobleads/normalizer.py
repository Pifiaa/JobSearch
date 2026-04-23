import hashlib

from scraping.parsers.location import parse_location
from scraping.parsers.modality import parse_modality
from scraping.parsers.salary import parse_salary
from scraping.parsers.text import is_blacklisted


def normalize(raw: dict, blacklist: list[str]) -> dict | None:
    if not raw.get("title"):
        return None

    company = _clean_short_text(raw.get("company"))
    if company and is_blacklisted(company, blacklist):
        return None

    description = raw.get("description") or None
    city, department = parse_location(raw.get("city_raw", ""))

    return {
        "external_id": raw["external_id"],
        "title": _clean_short_text(raw["title"], 255),
        "company": company,
        "city": _clean_short_text(city),
        "department": _clean_short_text(department),
        "country": "CO",
        "modality": parse_modality(raw.get("modality_raw", "")).value,
        "salary_range": _clean_short_text(parse_salary(raw.get("salary_range", ""))),
        "description": _clean_description(description),
        "description_hash": hashlib.md5(description.encode()).hexdigest() if description else None,
        "url": raw["url"],
        "published_at": None,
    }


def _clean_short_text(value: str | None, limit: int = 255) -> str | None:
    if not value:
        return None
    cleaned = " ".join(value.split()).strip(" -|")
    if not cleaned:
        return None
    return cleaned[:limit]


def _clean_description(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = " ".join(value.split())
    return cleaned[:12000]
