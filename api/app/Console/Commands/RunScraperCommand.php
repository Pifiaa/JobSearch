<?php

namespace App\Console\Commands;

use App\Models\Source;
use App\Jobs\ScrapeSourceJob;
use Illuminate\Console\Command;

class RunScraperCommand extends Command
{
    protected $signature   = 'scraper:run-all';
    protected $description = 'Encola el scraping de todas las fuentes activas';

    public function handle(): void
    {
        $sources = Source::where('is_active', true)->get();

        foreach ($sources as $source) {
            ScrapeSourceJob::dispatch($source);
        }

        $this->info("Scraping encolado para {$sources->count()} fuentes.");
    }
}