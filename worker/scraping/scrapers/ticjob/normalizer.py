import hashlib
from scraping.parsers.location import parse_location
from scraping.parsers.modality import parse_modality
from scraping.parsers.salary import parse_salary
from scraping.parsers.text import is_blacklisted

MAX_LOCATION_PARTS = 2

def normalize(raw: dict, blacklist: list[str]) -> dict | None:
    if not raw.get("title"):
        return None

    company = raw.get("company", "") or ""
    if company and is_blacklisted(company, blacklist):
        return None

    location_raw = raw.get("location_raw", "") or ""
    if location_raw.count(",") > MAX_LOCATION_PARTS:
        city, department = None, None
    else:
        city, department = parse_location(location_raw)

    return {
        "external_id":      raw["external_id"],
        "title":            raw["title"],
        "company":          company or None,
        "city":             city,
        "department":       department,
        "country":          "CO",
        "modality":         parse_modality(raw["modality_raw"]).value,
        "salary_range":     parse_salary(raw["salary_range"]),
        "description":      raw["description"] or None,
        "description_hash": hashlib.md5(raw["description"].encode()).hexdigest() if raw["description"] else None,
        "url":              raw["url"],
        "published_at":     raw.get("published_at_raw") or None,
    }