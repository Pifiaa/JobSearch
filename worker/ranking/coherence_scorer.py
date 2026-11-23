import json
import os
import requests
from core.logger import log

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "60"))

_PROMPT_TEMPLATE = """Vas a clasificar si una oferta de empleo pertenece a UNA sola familia profesional, o si en realidad exige responsabilidades de 2 o más familias distintas (un "todólogo" disfrazado de un solo cargo).

FAMILIAS PROFESIONALES (usa exactamente esta lista, no inventes otras):
A. Desarrollo y operación de software — incluye: frontend, backend, full stack, apps móviles, arquitectura de software, DevOps, CI/CD, bases de datos, control de calidad/testing, seguridad informática/ciberseguridad, y administración de servidores/VPS/infraestructura CUANDO es para alojar o soportar el software que la misma persona desarrolla. Todo esto cuenta como UNA sola familia (A), sin importar cuántas de estas tareas combine.
B. Marketing y comunicación (email marketing, redes sociales, SEO/SEM, publicidad, contenido)
C. Ventas y atención comercial
D. Contabilidad y finanzas
E. Diseño gráfico o multimedia NO relacionado con código (branding, ilustración, edición de video)
F. Recursos humanos
G. Administración funcional de un ERP/CRM como usuario de negocio (configurar módulos de ventas, inventario, facturación — distinto de programarlos, eso sería A)
H. Gestión de proyectos o producto como rol dedicado (Scrum Master, PM de tiempo completo — NO cuenta liderar o dar mentoría al propio equipo técnico, eso sigue siendo A)

REGLA: vacante_coherente = false únicamente si la vacante exige responsabilidades reales de 2 o más familias DISTINTAS de esta lista (o si mezcla títulos de cargos claramente distintos, ej: "Desarrollador / Auxiliar Contable / Vendedor"). Si todo lo que pide cae dentro de una sola familia — por técnicamente amplio que sea — es coherente, aunque combine muchas tecnologías o tareas.

Ejemplos ya resueltos:

Ejemplo 1:
VACANTE: "Desarrollador Full Stack: React en frontend, Node.js en backend, despliegue y mantenimiento del VPS donde corre la app, y diseño de la base de datos PostgreSQL."
RESPUESTA: {{"vacante_coherente": true, "cargos_detectados": ["Desarrollador Full Stack"], "justificacion": "Frontend, backend, despliegue del propio VPS y base de datos son todas tareas de la familia A (desarrollo y operación de software)."}}

Ejemplo 2:
VACANTE: "Desarrollador Web para gestionar nuestra tienda WordPress/WooCommerce, administrar el servidor VPS y Plesk, configurar y mantener nuestro ERP Odoo (ventas, inventario), y gestionar campañas de email marketing en Brevo."
RESPUESTA: {{"vacante_coherente": false, "cargos_detectados": ["Desarrollador Web (familia A)", "Administrador funcional de ERP (familia G)", "Especialista en email marketing (familia B)"], "justificacion": "Combina desarrollo/infraestructura (A) con administración funcional de un ERP de negocio (G) y marketing (B): tres familias distintas."}}

Ejemplo 3:
VACANTE: "Desarrollador / Auxiliar Contable / Vendedor para pyme en crecimiento."
RESPUESTA: {{"vacante_coherente": false, "cargos_detectados": ["Desarrollador (A)", "Auxiliar Contable (D)", "Vendedor (C)"], "justificacion": "El anuncio mezcla explícitamente tres títulos de cargos de familias distintas."}}

Ahora evalúa esta vacante real:

VACANTE:
{description}

Responde ÚNICAMENTE con un objeto JSON con exactamente estas claves:
- "vacante_coherente": true o false, según la regla de arriba
- "cargos_detectados": lista de las familias/roles identificados, indicando la letra de familia entre paréntesis (un solo elemento si es coherente)
- "justificacion": explicación breve (máximo 2 frases) citando las familias involucradas"""


def score_coherence(description: str) -> dict:
    """
    Evaluación de coherencia de la vacante (no depende del CV).
    Se ejecuta una sola vez por vacante, al momento del scraping.
    En caso de error retorna coherente=None (no bloquea la persistencia).
    """
    if not description:
        return _empty()

    prompt = _PROMPT_TEMPLATE.format(description=description[:3000])

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

        return {
            "vacante_coherente": bool(parsed.get("vacante_coherente", True)),
            "coherence_detail": {
                "cargos_detectados": parsed.get("cargos_detectados", []),
                "justificacion": parsed.get("justificacion", ""),
            },
        }

    except requests.exceptions.Timeout:
        log(f"[ranking] coherence_scorer timeout ({OLLAMA_TIMEOUT}s) — evaluacion omitida")
        return _empty()
    except requests.exceptions.ConnectionError:
        log(f"[ranking] coherence_scorer sin conexion a Ollama ({OLLAMA_URL}) — evaluacion omitida")
        return _empty()
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        log(f"[ranking] coherence_scorer parse error: {e} — evaluacion omitida")
        return _empty()


def _empty() -> dict:
    return {
        "vacante_coherente": None,
        "coherence_detail": None,
    }
