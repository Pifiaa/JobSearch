<?php

namespace App\Jobs;

use App\Models\Source;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Log;

class ScrapeAllSourcesJob implements ShouldQueue
{
    use Queueable;

    public function handle(): void
    {
        $sources = Source::where('is_active', true)->get();

        Log::info("ScrapeAllSourcesJob: encolando {$sources->count()} fuentes.");

        foreach ($sources as $source) {
            ScrapeSourceJob::dispatch($source);
        }
    }
}