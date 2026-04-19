import json
import sys
from ranking.cv_reader import read_cv_text
from ranking.keyword_extractor import extract_keywords
from ranking.scorer import score_vacancy
from ranking.semantic_scorer import score_semantic
from core.logger import log


def main():
    try:
        raw = sys.stdin.read()
        vacancies = json.loads(raw)
    except Exception as e:
        print(json.dumps({"error": f"JSON inválido: {e}"}))
        sys.exit(1)

    cv_text = read_cv_text()
    cv_keywords = extract_keywords(cv_text)

    results = []
    for v in vacancies:
        description = v.get("description") or ""
        keyword_result = score_vacancy(cv_keywords, description)
        semantic_score = score_semantic(cv_text, description)
        results.append({
            "id":                 v["id"],
            "cv_score":           keyword_result["cv_score"],
            "cv_score_semantic":  semantic_score,
            "cv_keywords_detail": keyword_result["cv_keywords_detail"],
        })

    log(f"[rescorer] Re-scored {len(results)} vacantes")
    print(json.dumps({"results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()