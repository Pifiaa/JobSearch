import json
import os
import requests
from core.logger import log

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "60"))

_PROMPT_TEMPLATE = """Analiza la compatibilidad entre este CV y esta vacante de empleo.

CV:
{cv_text}

VACANTE:
{description}

Responde con un objeto JSON con exactamente estas claves:
- "score": número entero entre 0 y 100 representando compatibilidad global
- "matched": lista de tecnologías/habilidades que el CV tiene y la vacante pide
- "missing": lista de tecnologías/habilidades que pide la vacante y el CV no tiene"""


def score_llm(cv_text: str, description: str) -> dict:
    """
    Capa 3 — scoring cualitativo vía LLM local (Ollama).
    Retorna dict con score (0-100), matched y missing.
    En caso de error retorna score 0 y listas vacías (no interrumpe el pipeline).
    """
    if not cv_text or not description:
        return _empty()

    prompt = _PROMPT_TEMPLATE.format(
        cv_text=cv_text[:3000],
        description=description[:2000],
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            },
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
        raw = response.json().get("response", "")
        parsed = json.loads(raw)

        score = int(parsed.get("score", 0))
        score = max(0, min(100, score))  # clamp 0-100

        return {
            "llm_score": score,
            "llm_detail": {
                "matched": parsed.get("matched", []),
                "missing": parsed.get("missing", []),
            },
        }

    except requests.exceptions.Timeout:
        log(f"[ranking] llm_scorer timeout ({OLLAMA_TIMEOUT}s) — score omitido")
        return _empty()
    except requests.exceptions.ConnectionError:
        log(f"[ranking] llm_scorer sin conexión a Ollama ({OLLAMA_URL}) — score omitido")
        return _empty()
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        log(f"[ranking] llm_scorer parse error: {e} — score omitido")
        return _empty()


def _empty() -> dict:
    return {
        "llm_score": 0,
        "llm_detail": {"matched": [], "missing": []},
    }