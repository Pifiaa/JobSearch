import hashlib

from scraping.parsers.modality import parse_modality
from scraping.parsers.salary import parse_salary


def normalize(raw: dict, blacklist: list[str]) -> dict | None:
    if not raw.get("title"):
        return None

    description = raw.get("description") or _build_description(raw)
    modality_raw = "remoto" if raw.get("telework_raw") == "1" else raw.get("telework_raw", "")

    return {
        "external_id": raw["external_id"],
        "title": raw["title"],
        "company": "Agencia Pública de Empleo SENA",
        "city": raw.get("city") or None,
        "department": raw.get("department") or None,
        "country": "CO",
        "modality": parse_modality(modality_raw).value,
        "salary_range": parse_salary(raw.get("salary_range", "")),
        "description": description or None,
        "description_hash": hashlib.md5(description.encode()).hexdigest() if description else None,
        "url": raw["url"],
        "published_at": raw.get("published_at_raw") or None,
    }


def _build_description(raw: dict) -> str:
    parts = [
        raw.get("title"),
        raw.get("area"),
        raw.get("occupational_area"),
        f"{raw.get('experience_months')} meses de experiencia" if raw.get("experience_months") else None,
        f"Contrato {raw.get('contract_type')}" if raw.get("contract_type") else None,
        f"Jornada {raw.get('schedule_raw')}" if raw.get("schedule_raw") else None,
    ]
    return ". ".join(part for part in parts if part)
