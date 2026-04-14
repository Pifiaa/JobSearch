<?php

namespace App\Jobs;

use App\Models\Source;
use App\Services\ScraperService;
use App\Services\VacancyPersistenceService;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;

class ScrapeSourceJob implements ShouldQueue
{
    use Queueable;

    public int $timeout = 3600;
    public int $tries = 1;

    public function __construct(
        private Source $source,
        private bool $mock = false,
    ) {}

    public function handle(ScraperService $scraper, VacancyPersistenceService $persistence): void
    {
        Log::info("ScrapeSourceJob: iniciando", ['source' => $this->source->name]);

        $vacancies = $scraper->run($this->source, $this->mock);

        DB::reconnect();

        $result = $persistence->persistMany($vacancies, $this->source);

        Log::info("ScrapeSourceJob: finalizado", [
            'source'  => $this->source->name,
            'created' => $result['created'],
            'skipped' => $result['skipped'],
        ]);
    }
}