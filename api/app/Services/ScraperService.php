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

        // Antes se redirigía stderr a /dev/null, lo que ocultaba la causa
        // real de cualquier fallo (docker exec sin acceso al daemon, socket
        // muerto, worker caído, etc.) detrás de un genérico "no devolvió
        // output". Ahora se captura por separado para poder reportarla.
        $stderrFile = tempnam(sys_get_temp_dir(), 'scraper_stderr_');

        if ($mock) {
            $fullCommand = sprintf(
                'docker exec jobsearch_worker sh -c %s 2>%s',
                escapeshellarg($innerCommand),
                escapeshellarg($stderrFile)
            );
        } else {
            $fullCommand = sprintf(
                'docker exec -e SCRAPER_CONFIG=%s jobsearch_worker sh -c %s 2>%s',
                escapeshellarg($config),
                escapeshellarg($innerCommand),
                escapeshellarg($stderrFile)
            );
        }

        exec($fullCommand, $outputLines, $exitCode);
        $output = implode("\n", $outputLines);
        $stderr = trim((string) @file_get_contents($stderrFile));
        @unlink($stderrFile);

        if ($exitCode !== 0 || $output === '') {
            Log::error("ScraperService: fallo al ejecutar el worker", [
                'source'    => $source->name,
                'exit_code' => $exitCode,
                'stderr'    => $stderr,
            ]);

            $detail = $stderr !== '' ? $stderr : "sin salida (exit code {$exitCode})";
            throw new RuntimeException("El worker no devolvió output. Detalle: {$detail}");
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