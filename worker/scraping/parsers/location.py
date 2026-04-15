def parse_location(city_raw: str) -> tuple[str | None, str | None]:
    city_raw = city_raw.strip()
    if not city_raw:
        return None, None
    parts = city_raw.split(",", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return city_raw, None