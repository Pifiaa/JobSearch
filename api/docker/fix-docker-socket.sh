#!/bin/sh
set -e

# El socket de Docker montado desde el host pertenece a root; PHP-FPM corre
# como www-data (correcto, FPM se niega a arrancar como root). Este script
# corre una sola vez, como root, al iniciar el contenedor, y solo ajusta el
# permiso del socket — no cambia el usuario del pool de PHP-FPM.
if [ -S /var/run/docker.sock ]; then
    chmod 666 /var/run/docker.sock 2>/dev/null || true
fi

exec docker-php-entrypoint "$@"
