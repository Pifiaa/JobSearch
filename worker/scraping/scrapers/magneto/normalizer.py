import hashlib
from scraping.parsers.location import parse_location
from scraping.parsers.modality import parse_modality
from scraping.parsers.salary import parse_salary
from scraping.parsers.text import is_blacklisted


def normalize(raw: dict, blacklist: list[str]) -> dict | None:
    if not raw.get("title"):
        return None

    company = raw.get("company", "") or ""
    if company and is_blacklisted(company, blacklist):
        return None

    # Magneto no expone modalidad en el listado — inferir desde ciudad
    modality_raw = ""
    city_raw = raw.get("city_raw", "") or ""
    if "remoto" in city_raw.lower():
        modality_raw = "remoto"

    city, department = parse_location(city_raw)

    description = raw.get("description") or None

    return {
        "external_id":      raw["external_id"],
        "title":            raw["title"],
        "company":          company or None,
        "city":             city,
        "department":       department,
        "country":          "CO",
        "modality":         parse_modality(modality_raw).value,
        "salary_range":     parse_salary(raw.get("salary_raw", "")),
        "description":      description,
        "description_hash": hashlib.md5(description.encode()).hexdigest() if description else None,
        "url":              raw["url"],
        "published_at":     None,
    }