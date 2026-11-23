<?php

namespace App\Console\Commands;

use App\Models\Vacancy;
use App\Services\TelegramService;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

class CleanOldVacanciesCommand extends Command
{
    protected $signature   = 'vacancies:clean-old {--days=15 : Días de antigüedad para desactivar}';
    protected $description = 'Desactiva vacantes nuevas con más de N días sin interacción';

    public function handle(TelegramService $telegram): void
    {
        $days = (int) $this->option('days');

        $count = Vacancy::where('status', 'nueva')
            ->where('is_active', true)
            ->where('scraped_at', '<', now()->subDays($days))
            ->update(['is_active' => false]);

        Log::info("CleanOldVacanciesCommand: vacantes desactivadas", [
            'count' => $count,
            'days'  => $days,
        ]);

        $this->info("Vacantes desactivadas: {$count}");

        // Solo notifica si de verdad desactivó algo — evita ruido diario en
        // Telegram cuando no hay nada que limpiar.
        if ($count > 0) {
            $telegram->send(
                "🧹 <b>Limpieza de vacantes</b>\n" .
                "Se desactivaron {$count} vacantes con más de {$days} días sin interacción."
            );
        }
    }
}