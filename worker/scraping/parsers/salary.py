INVALID_VALUES = {"a convenir", "0", ""}


def parse_salary(salary_raw: str) -> str | None:
    salary = salary_raw.strip()
    if salary.lower() in INVALID_VALUES:
        return None
    return salary