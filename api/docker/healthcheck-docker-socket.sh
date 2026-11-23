#!/bin/sh
# Healthcheck para api/horizon/scheduler: valida que el `docker exec` hacia
# jobsearch_worker sigue funcionando. Si el daemon de Docker del host se
# reinició después de que este contenedor arrancó, el socket bind-mounted
# queda apuntando a un inodo muerto y `docker exec` empieza a fallar con
# "Cannot connect to the Docker daemon" — sin que el contenedor se caiga
# (php-fpm / horizon / el loop del scheduler siguen vivos).
#
# Este script se usa como HEALTHCHECK en docker-compose.yml. Combinado con
# el servicio `autoheal`, un fallo aquí hace que Docker reinicie el
# contenedor automáticamente, lo cual le da un bind-mount fresco del socket.
docker exec jobsearch_worker echo ok >/dev/null 2>&1
