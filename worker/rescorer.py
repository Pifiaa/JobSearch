import json
import os
import sys
from ranking.cv_reader import read_cv_text
from ranking.keyword_extractor import extract_keywords
from ranking.scorer import score_vacancy
from ranking.semantic_scorer import score_semantic
from ranking.llm_scorer import score_llm
from core.logger import log

LLM_ENABLED       = os.environ.get("LLM_ENABLED", "true").lower() == "true"
LLM_MIN_KEYWORDS  = int(os.environ.get("LLM_MIN_KEYWORDS", "2"))   # mínimo de keywords para llamar al LLM


def main():
    try:
        raw = sys.stdin.read()
        vacancies = json.loads(raw)
    except Exception as e:
        print(json.dumps({"error": f"JSON inválido: {e}"}))
        sys.exit(1)

    cv_text    = read_cv_text()
    cv_keywords = extract_keywords(cv_text)

    log(f"[rescorer] LLM habilitado: {LLM_ENABLED} | umbral keywords: {LLM_MIN_KEYWORDS}")

    results = []
    llm_calls = 0

    for v in vacancies:
        description = v.get("description") or ""

        # Capa 1 — keywords deterministas
        keyword_result = score_vacancy(cv_keywords, description)

        # Capa 2 — similitud semántica spaCy
        semantic_score = score_semantic(cv_text, description)

        # Capa 3 — LLM solo si la vacante supera el umbral mínimo de keywords
        # Evita gastar 20s en vacantes que claramente no aplican
        use_llm = LLM_ENABLED and keyword_result["cv_score"] >= LLM_MIN_KEYWORDS
        if use_llm:
            llm_result = score_llm(cv_text, description)
            llm_calls += 1
        else:
            llm_result = {"llm_score": None, "llm_detail": None}

        results.append({
            "id":                 v["id"],
            "cv_score":           keyword_result["cv_score"],
            "cv_score_semantic":  semantic_score,
            "llm_score":          llm_result["llm_score"],
            "cv_keywords_detail": keyword_result["cv_keywords_detail"],
            "llm_detail":         llm_result["llm_detail"],
        })

    log(f"[rescorer] Re-scored {len(results)} vacantes | LLM calls: {llm_calls}")
    print(json.dumps({"results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()