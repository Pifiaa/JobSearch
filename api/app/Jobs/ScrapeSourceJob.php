<?php

namespace App\Jobs;

use App\Models\Source;
use App\Models\Vacancy;
use App\Services\ScraperService;
use App\Services\TelegramService;
use App\Services\VacancyPersistenceService;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class ScrapeSourceJob implements ShouldQueue
{
    use Queueable;

    public int $timeout = 3600;
    public int $tries   = 1;

    public function __construct(
        private Source $source,
        private bool   $mock = false,
    ) {}

    public function handle(
        ScraperService $scraper,
        VacancyPersistenceService $persistence,
        TelegramService $telegram,
    ): void {
        Log::info("ScrapeSourceJob: iniciando", ['source' => $this->source->name]);

        $vacancies = $scraper->run($this->source, $this->mock);

        DB::reconnect();

        $result = $persistence->persistMany($vacancies, $this->source);

        Log::info("ScrapeSourceJob: finalizado", [
            'source'  => $this->source->name,
            'created' => $result['created'],
            'skipped' => $result['skipped'],
        ]);

        $this->notify($result, $telegram);
    }

    private function notify(array $result, TelegramService $telegram): void
    {
        $threshold = (float) config('services.telegram.threshold', 2.0);

        $top = collect();

        if (!empty($result['createdIds'])) {
            $top = Vacancy::whereIn('id', $result['createdIds'])
                ->whereNotNull('cv_score')
                ->whereNotNull('cv_score_semantic')
                ->orderByRaw('(cv_score * 0.6 + cv_score_semantic * 0.4) DESC')
                ->get()
                ->filter(fn($v) => ($v->cv_score * 0.6 + $v->cv_score_semantic * 0.4) >= $threshold)
                ->take(20);
        }

        $lines   = [];
        $lines[] = "✅ <b>{$this->source->name}</b> — {$result['created']} nuevas, {$top->count()} relevantes";

        foreach ($top as $v) {
            $company = $v->company ?? 'Empresa no especificada';
            $city    = $v->city    ?? 'Sin ciudad';
            $score   = round($v->cv_score * 0.6 + $v->cv_score_semantic * 0.4, 2);
            $lines[] = "";
            $lines[] = "⭐ <b>{$score}</b> · {$v->title}";
            $lines[] = "   {$company} · {$city}";
            $lines[] = "   {$v->url}";
        }

        $telegram->send(implode("\n", $lines));
    }
}