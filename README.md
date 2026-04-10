# JobSearch

Agregador personal de vacantes con filtros, ranking textual y tracking básico.

Herramienta de uso personal para centralizar vacantes de múltiples fuentes, normalizarlas, rankearlas por relevancia al perfil y hacer seguimiento básico desde una UI simple.

## Stack

| Capa | Tecnología |
|---|---|
| Orquestador / API | Laravel 11 + Horizon |
| Frontend | React 18 + Vite + TailwindCSS |
| Worker | Python 3.12 — scraping + ranking/NLP |
| Base de datos | PostgreSQL 16 |
| Colas | Redis 7 + Laravel Horizon |
| Infraestructura | Docker Compose |

## Arquitectura

```
jobsearch/
├── api/        → Laravel 11 — orquestador central y API única
├── web/        → React 18 + Vite — solo habla con Laravel
├── worker/     → Python CLI — scraping + ranking/NLP
└── docker/     → configs Nginx
```

**Principios:**
- Laravel es el único punto de entrada del frontend.
- El worker Python no expone API ni habla con la BD directamente.
- El worker recibe argumentos CLI y devuelve JSON por stdout.
- Laravel captura el stdout, valida y persiste en PostgreSQL.
- Redis + Horizon para todo lo async.

## Levantar el proyecto

```bash
# Infraestructura base
docker compose up -d

# API + Nginx + Horizon
docker compose --profile app up -d

# Frontend
docker compose --profile web up -d
```