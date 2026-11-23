import json
import sys
from ranking.cv_reader import read_cv_text
from ranking.cv_tailor import tailor_cv
from core.logger import log


def main():
    try:
        payload = json.loads(sys.stdin.read())
        description = payload["description"]
    except Exception as e:
        print(json.dumps({"error": f"JSON inválido: {e}"}))
        sys.exit(1)

    cv_text = read_cv_text()
    result = tailor_cv(cv_text, description)

    log(f"[tailor] resumen generado ({len(result.get('resumen_profesional', ''))} chars, error={result.get('error')})")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
