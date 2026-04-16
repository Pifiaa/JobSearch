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

    city, department = parse_location(raw.get("city_raw", ""))

    return {
        "external_id":      raw["external_id"],
        "title":            raw["title"],
        "company":          company or None,
        "city":             city,
        "department":       department,
        "country":          "CO",
        "modality":         parse_modality(raw.get("modality_raw", "")).value,
        "salary_range":     parse_salary(raw.get("salary_range", "")),
        "description":      raw.get("description") or None,
        "description_hash": hashlib.md5(raw["description"].encode()).hexdigest() if raw.get("description") else None,
        "url":              raw["url"],
        "published_at":     raw.get("published_at_raw") or None,
    }