# Patch: CV a medida por vacante (on-demand)

Todos los archivos respetan la ruta relativa dentro de tu proyecto `jobsearch/`.
Copia cada carpeta encima de la tuya (mismo path) y sigue estos pasos.

## 1. Archivos nuevos (copiar tal cual)
- worker/ranking/cv_tailor.py
- worker/tailor.py
- api/database/migrations/2026_08_05_000000_add_tailored_cv_to_vacancies.php
- api/app/Services/CvTailorService.php
- api/app/Http/Controllers/CvTailorController.php
- api/resources/views/pdf/cv-cover.blade.php
- web/src/api/cvTailor.ts
- web/src/components/vacancy/TailorCvPanel.tsx
- docker/nginx/default.conf (reemplaza al tuyo, agrega `fastcgi_read_timeout 240s`)
- web/docker/web.conf (reemplaza al tuyo, agrega `proxy_read_timeout 240s`)
- api/Dockerfile (reemplaza al tuyo)
- api/docker/fix-docker-socket.sh (nuevo)

### ⚠️ Fix de permisos del socket de Docker (v4, versión correcta)
La v3 de este patch estaba mal: intentaba hacer correr PHP-FPM como root,
pero PHP-FPM se niega a arrancar así (`please specify user and group other
than root` → el contenedor `api` nunca levantaba → `nginx` no podía resolver
el hostname `api` → 502 en todo). Revertido.

El fix correcto: PHP-FPM se queda como `www-data` (como debe ser), y un
script de arranque (`fix-docker-socket.sh`) le da permiso al socket de
Docker una sola vez, al iniciar el contenedor, antes de lanzar PHP-FPM.

**Secuencia completa, en este orden exacto:**
```bash
docker compose --profile app up -d --build api horizon scheduler
docker compose --profile app restart nginx
```
El segundo comando es obligatorio siempre que `api` se reconstruya o
reinicie: `nginx` cachea la IP del contenedor `api` al arrancar y no la
refresca sola.

Verifica que `api` esté realmente arriba antes de seguir:
```bash
docker compose --profile app ps
```
Debe aparecer `jobsearch_api` como `Up`. Si no aparece, el contenedor sigue
crasheando — pega `docker compose --profile app logs api --tail=30` antes de
seguir probando el botón, así evitamos otra vuelta de prueba y error.

### ⚠️ Fix de timeout (v2 de este patch)
Si ya habías instalado la v1 y te da `error: timeout` en el botón: la generación
en GPUs de 6GB (RTX 2060) tarda más de los 60s que nginx corta por defecto en
2 saltos distintos (`web` → `nginx` → `api`). Este patch ya trae:
- Prompt más corto en `cv_tailor.py` (menos texto = generación más rápida) +
  límite de `num_predict=400` tokens para acotar el peor caso.
- `OLLAMA_TAILOR_TIMEOUT` subido a 180s por defecto.
- `fastcgi_read_timeout 240s` en `docker/nginx/default.conf`.
- `proxy_read_timeout 240s` en `web/docker/web.conf`.

Después de copiar estos dos `.conf`:
```bash
docker compose --profile app restart nginx        # default.conf es bind mount, con restart basta
docker compose --profile app up -d --build web     # web.conf está horneado en la imagen, necesita rebuild
```

## 2. Archivos que REEMPLAZAN a los tuyos (ya traen tus cambios existentes + lo nuevo)
- api/routes/api.php
- api/app/Models/Vacancy.php
- web/src/types/index.ts
- web/src/components/vacancy/VacancyDetail.tsx

Revísalos con un diff antes de sobreescribir por si tenías cambios propios desde
que me pasaste el zip.

## 3. Dependencias PHP (dentro del contenedor/carpeta api)
```bash
docker compose --profile app exec api composer require barryvdh/laravel-dompdf phpoffice/phpword setasign/fpdi setasign/fpdi-fpdf
```
`setasign/fpdi` por sí solo NO incluye una clase `FPDF` (la necesita como base
para poder escribir el PDF de salida) — `setasign/fpdi-fpdf` es el paquete
que la provee. Sin este último, `new Fpdi()` falla con
`Class "FPDF" not found`. No hace falta rebuild de imagen, es bind mount:
solo `composer require` y listo, no hay que reiniciar `api`.

## 4. Migración
```bash
php artisan migrate
```

## 5. Variables de entorno del worker (opcional, ya tienen defaults sensatos)
```
OLLAMA_URL=http://host.docker.internal:11434/api/generate
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TAILOR_TIMEOUT=90
```

## 6. Ruta del CV dentro del contenedor Laravel
`CvTailorService::$cvPath` apunta a:
```
/home/dev/projects/jobsearch/worker/data/cv.pdf
```
Ajusta esa constante si tu volumen Docker monta el CV en otra ruta visible
desde el contenedor de la API (no del worker) — Laravel necesita leer ese
archivo directamente para el merge con FPDI, no vía docker exec.

## 7. Probar el worker suelto antes de integrarlo (recomendado)
```bash
docker exec -i jobsearch_worker sh -c "cd /app && python tailor.py" <<'EOF'
{"description": "Buscamos desarrollador PHP/Laravel con React, 3+ años de experiencia..."}
EOF
```
Si responde JSON con `resumen_profesional`, `habilidades_destacadas`, etc.,
el pipeline del worker está listo y el problema (si algo falla después) está
en la capa Laravel/frontend, no en el LLM.

## Notas de diseño
- **Nada se ejecuta solo.** El endpoint `/vacancies/{id}/tailor-cv` es POST
  manual, disparado únicamente por el botón "Generar CV a medida" en el
  detalle de la vacante. No hay job en cola ni scheduler.
- **Anti-alucinación.** El prompt en `cv_tailor.py` obliga al modelo a separar
  lo que sí está en tu CV de lo que la vacante pide y no tienes ("brechas").
  Aun así, revisa el resultado antes de postular — un LLM local de 8B puede
  cometer errores de redacción.
- **El PDF exportado no reescribe tu CV.** Antepone una portada generada
  (resumen + skills destacadas para esa vacante) a tu `cv.pdf` real, que queda
  intacto en las páginas siguientes.
- `TailorCvPanel.onGenerated` reutiliza el callback `onStatusChange` que ya
  tenía `VacancyDetail` para refrescar el estado local sin tocar el resto del
  componente — funcionalmente correcto, pero si prefieres un callback con
  nombre propio (`onTailoredCvGenerated`) es un cambio de 3 líneas.
