import json
import os
import requests
from core.logger import log

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TAILOR_TIMEOUT = int(os.environ.get("OLLAMA_TAILOR_TIMEOUT", "180"))
OLLAMA_TAILOR_NUM_PREDICT = int(os.environ.get("OLLAMA_TAILOR_NUM_PREDICT", "400"))

# Prompt deliberadamente más corto que el de scoring: en GPUs de 6GB (ej. RTX 2060)
# cada palabra de salida cuesta tiempo real. Pedimos menos ítems y frases cortas.
_PROMPT = """Adapta el ENFOQUE de este CV real a una vacante, SIN inventar experiencia,
cargos, empresas, años ni tecnologías que no aparezcan en el CV.

CV:
{cv_text}

VACANTE:
{description}

Reglas: todo debe basarse solo en el CV. Lo que la vacante pide y el CV no cubre va
SOLO en "brechas". Sé breve y concreto, sin relleno.

JSON con estas claves:
- "resumen_profesional": 2-3 líneas
- "habilidades_destacadas": máx 6 items
- "sugerencias_bullets": máx 3 items, cada uno una frase corta
- "brechas": máx 4 items
"""


def tailor_cv(cv_text: str, description: str) -> dict:
    """
    Genera sugerencias de adaptación de CV a una vacante puntual, vía Ollama.
    No modifica el CV real; devuelve texto derivado que Laravel persiste
    y usa para maquetar la portada del PDF/Word exportable.
    """
    if not cv_text or not description:
        return _empty("input_vacio")

    prompt = _PROMPT.format(cv_text=cv_text[:4000], description=description[:2500])

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.2, "num_predict": OLLAMA_TAILOR_NUM_PREDICT},
            },
            timeout=OLLAMA_TAILOR_TIMEOUT,
        )
        response.raise_for_status()
        raw = response.json().get("response", "")
        parsed = json.loads(raw)

        return {
            "resumen_profesional":    parsed.get("resumen_profesional", ""),
            "habilidades_destacadas": parsed.get("habilidades_destacadas", []),
            "sugerencias_bullets":    parsed.get("sugerencias_bullets", []),
            "brechas":                parsed.get("brechas", []),
            "error": None,
        }

    except requests.exceptions.Timeout:
        log(f"[cv_tailor] timeout ({OLLAMA_TAILOR_TIMEOUT}s) — generación omitida")
        return _empty("timeout")
    except requests.exceptions.ConnectionError:
        log(f"[cv_tailor] sin conexión a Ollama ({OLLAMA_URL})")
        return _empty("sin_conexion")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        log(f"[cv_tailor] parse error: {e}")
        return _empty("parse_error")


def _empty(error: str) -> dict:
    return {
        "resumen_profesional": "",
        "habilidades_destacadas": [],
        "sugerencias_bullets": [],
        "brechas": [],
        "error": error,
    }
