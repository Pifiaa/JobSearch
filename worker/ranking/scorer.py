import re
from ranking.keyword_extractor import _apply_aliases


def score_vacancy(cv_keywords: list[str], description: str) -> dict:
    normalized = _apply_aliases(description.lower())

    matched = [kw for kw in cv_keywords if re.search(rf"\b{re.escape(kw)}\b", normalized)]
    missing = [kw for kw in cv_keywords if kw not in matched]

    return {
        "cv_score": len(matched),
        "cv_keywords_detail": {
            "matched": matched,
            "missing": missing,
        },
    }