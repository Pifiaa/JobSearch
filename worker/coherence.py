import json
import sys
from ranking.coherence_scorer import score_coherence
from core.logger import log


def main():
    try:
        raw = sys.stdin.read()
        vacancies = json.loads(raw)
    except Exception as e:
        print(json.dumps({"error": f"JSON invalido: {e}"}))
        sys.exit(1)

    results = []

    for v in vacancies:
        description = v.get("description") or ""
        coherence = score_coherence(description)
        results.append({
            "id": v["id"],
            **coherence,
        })

    log(f"[coherence] Evaluadas {len(results)} vacantes")
    print(json.dumps({"results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
