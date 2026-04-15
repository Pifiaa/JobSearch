import re
from core.logger import log


TECH_KEYWORDS: list[str] = [
    # Lenguajes
    "php", "python", "javascript", "typescript", "nodejs", "go", "java", "c#", "sql",
    # Frameworks / librerías
    "laravel", "react", "nextjs", "vue", "angular", "fastapi", "django", "flask",
    "tailwind", "bootstrap", "jquery",
    # Bases de datos
    "postgresql", "mysql", "sqlite", "redis", "mongodb",
    # Herramientas / infra
    "docker", "git", "linux", "nginx", "composer", "npm", "vite",
    "horizon", "eloquent", "sanctum",
    # Conceptos
    "rest", "api", "solid", "mvc", "orm", "crud",
]

KEYWORD_ALIASES: dict[str, str] = {
    "java script": "javascript",
    "type script": "typescript",
    "node js": "nodejs",
    "node.js": "nodejs",
    "react js": "react",
    "react.js": "react",
    "vue js": "vue",
    "vue.js": "vue",
    "next js": "nextjs",
    "next.js": "nextjs",
    "postgres": "postgresql",
    "postgre": "postgresql",
}


def _apply_aliases(text: str) -> str:
    for alias, canonical in KEYWORD_ALIASES.items():
        text = text.replace(alias, canonical)
    return text


def extract_keywords(text: str) -> list[str]:
    normalized = _apply_aliases(text.lower())
    found = [kw for kw in TECH_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", normalized)]
    log(f"[ranking] keywords encontradas: {found}")
    return found