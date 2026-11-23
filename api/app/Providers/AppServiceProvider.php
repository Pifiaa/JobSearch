<?php

namespace App\Providers;

use App\Services\TelegramService;
use Illuminate\Queue\Events\JobFailed;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        Event::listen(JobFailed::class, function (JobFailed $event): void {
            $this->notifyJobFailure($event);
        });
    }

    /**
     * Notifica por Telegram cuando un job de la cola falla definitivamente.
     *
     * Sin esto, un fallo (ej. worker inaccesible, socket de Docker muerto,
     * error del scraper) solo queda registrado en `failed_jobs` y en los
     * logs, sin ninguna señal visible hasta que alguien nota que faltan
     * vacantes nuevas.
     */
    private function notifyJobFailure(JobFailed $event): void
    {
        $jobName = class_basename($event->job->resolveName());
        $queue   = $event->job->getQueue();
        $context = $this->extractJobContext($event->job);

        $reason = $event->exception->getMessage();
        if (mb_strlen($reason) > 300) {
            $reason = mb_substr($reason, 0, 300) . '…';
        }

        Log::error("JobFailed: {$jobName}", [
            'queue'     => $queue,
            'context'   => $context,
            'exception' => get_class($event->exception),
            'message'   => $event->exception->getMessage(),
        ]);

        try {
            $header = "🔴 <b>Job falló: {$jobName}</b>";
            if ($context !== null) {
                $header .= " ({$context})";
            }

            app(TelegramService::class)->send(
                "{$header}\n" .
                "Cola: {$queue}\n" .
                "Error: {$reason}"
            );
        } catch (\Throwable $e) {
            // Si Telegram mismo falla, no queremos que eso rompa el manejo
            // del fallo original del job; ya quedó en el log de arriba.
            Log::error('AppServiceProvider: no se pudo notificar el JobFailed por Telegram', [
                'error' => $e->getMessage(),
            ]);
        }
    }

    /**
     * Intenta identificar de qué está hablando el job fallido (ej. qué
     * Source estaba procesando ScrapeSourceJob) deserializando el comando
     * original desde el payload de la cola. Sin esto, la notificación de
     * fallo solo dice el nombre de la clase del job y no permite saber
     * cuál instancia específica falló.
     */
    private function extractJobContext(\Illuminate\Contracts\Queue\Job $job): ?string
    {
        try {
            $payload = $job->payload();
            $command = unserialize($payload['data']['command'] ?? '');

            if (!is_object($command)) {
                return null;
            }

            // Convención: cualquier job con una propiedad pública o privada
            // "source" (Eloquent Model con 'name', o string) se reporta.
            $ref = new \ReflectionObject($command);
            if ($ref->hasProperty('source')) {
                $prop = $ref->getProperty('source');
                $prop->setAccessible(true);
                $source = $prop->getValue($command);

                if (is_object($source) && isset($source->name)) {
                    return "source: {$source->name}";
                }
                if (is_string($source)) {
                    return "source: {$source}";
                }
            }

            return null;
        } catch (\Throwable) {
            return null;
        }
    }
}
