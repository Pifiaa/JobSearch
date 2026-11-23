FROM php:8.4-fpm

RUN apt-get update && apt-get install -y \
    git \
    unzip \
    libpq-dev \
    libzip-dev \
    docker.io \
    && docker-php-ext-install pdo pdo_pgsql pcntl zip \
    && pecl install redis \
    && docker-php-ext-enable redis \
    && rm -rf /var/lib/apt/lists/*

RUN echo "upload_max_filesize=10M\npost_max_size=10M" > /usr/local/etc/php/conf.d/uploads.ini

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Permite que PHP-FPM (que sigue corriendo como www-data) pueda usar el
# socket de Docker montado desde el host, sin correr el pool como root.
COPY docker/fix-docker-socket.sh /usr/local/bin/fix-docker-socket.sh
COPY docker/healthcheck-docker-socket.sh /usr/local/bin/healthcheck-docker-socket.sh
RUN chmod +x /usr/local/bin/fix-docker-socket.sh /usr/local/bin/healthcheck-docker-socket.sh
ENTRYPOINT ["/usr/local/bin/fix-docker-socket.sh"]
CMD ["php-fpm"]

WORKDIR /var/www/html
