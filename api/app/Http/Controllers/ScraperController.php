<?php

namespace App\Http\Controllers;

use App\Jobs\ScrapeAllSourcesJob;
use App\Jobs\ScrapeSourceJob;
use App\Models\Source;
use Illuminate\Http\JsonResponse;

class ScraperController extends Controller
{
    public function run(int $sourceId): JsonResponse
    {
        $source = Source::findOrFail($sourceId);

        ScrapeSourceJob::dispatch($source);

        return response()->json([
            'message' => "Job de scraping encolado para {$source->name}.",
        ]);
    }

    public function runAll(): JsonResponse
    {
        ScrapeAllSourcesJob::dispatch();

        return response()->json([
            'message' => "Job de scraping encolado para todas las fuentes activas.",
        ]);
    }
}