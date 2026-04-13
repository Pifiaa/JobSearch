import unicodedata


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().replace(" ", "")


def is_blacklisted(company: str, blacklist: list[str]) -> bool:
    normalized_blacklist = [normalize_text(entry) for entry in blacklist]
    company_normalized = normalize_text(company)
    return any(entry in company_normalized for entry in normalized_blacklist)