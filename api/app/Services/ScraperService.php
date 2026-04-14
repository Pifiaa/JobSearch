<?php

namespace App\Services;

use App\Models\Source;
use Illuminate\Support\Facades\Log;
use RuntimeException;

class ScraperService
{
    public function buildCommand(Source $source, bool $mock = false): string
    {
        if ($mock) {
            return sprintf(
                'python scraper.py --source %s --mock',
                escapeshellarg($source->name)
            );
        }

        return sprintf(
            'python scraper.py --source %s --url %s --config "$SCRAPER_CONFIG"',
            escapeshellarg($source->name),
            escapeshellarg($source->url)
        );
    }

    public function run(Source $source, bool $mock = false): array
    {
        $command = $this->buildCommand($source, $mock);
        $output  = $this->execute($command, $source, $mock);

        return $this->parse($output, $source->name);
    }

    private function execute(string $command, Source $source, bool $mock): string
    {
        $config = json_encode($source->headers ?? []);

        $innerCommand = "cd /app && {$command}";

        if ($mock) {
            $fullCommand = sprintf(
                'docker exec jobsearch_worker sh -c %s 2>/dev/null',
                escapeshellarg($innerCommand)
            );
        } else {
            $fullCommand = sprintf(
                'docker exec -e SCRAPER_CONFIG=%s jobsearch_worker sh -c %s 2>/dev/null',
                escapeshellarg($config),
                escapeshellarg($innerCommand)
            );
        }

        $output = shell_exec($fullCommand);

        if ($output === null) {
            throw new RuntimeException("El worker no devolvió output.");
        }

        return $output;
    }

    private function parse(string $output, string $sourceName): array
    {
        $data = json_decode($output, true);

        if (json_last_error() !== JSON_ERROR_NONE) {
            Log::error("ScraperService: JSON inválido del worker", [
                'source' => $sourceName,
                'error'  => json_last_error_msg(),
            ]);

            throw new RuntimeException("JSON inválido del worker para fuente: {$sourceName}");
        }

        if (!isset($data['vacancies']) || !is_array($data['vacancies'])) {
            throw new RuntimeException("El worker no devolvió el campo 'vacancies' para fuente: {$sourceName}");
        }

        return $data['vacancies'];
    }
}