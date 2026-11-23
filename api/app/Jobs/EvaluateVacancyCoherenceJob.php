<?php
namespace App\Jobs;
use App\Enums\VacancyStatus;
use App\Models\Vacancy;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Log;

class EvaluateVacancyCoherenceJob implements ShouldQueue
{
    use Queueable;

    public int $timeout = 900;
    public int $tries   = 2;

    public function __construct(private array $vacancyIds) {}

    public function handle(): void
    {
        if (empty($this->vacancyIds)) {
            return;
        }

        $vacancies = Vacancy::whereIn('id', $this->vacancyIds)
            ->whereNotNull('description')
            ->get(['id', 'description']);

        if ($vacancies->isEmpty()) {
            return;
        }

        Log::info("EvaluateVacancyCoherenceJob: evaluando", ['total' => $vacancies->count()]);

        $input   = json_encode($vacancies->toArray());
        $tmpFile = tempnam(sys_get_temp_dir(), 'coherence_') . '.json';
        file_put_contents($tmpFile, $input);

        $stderrFile = tempnam(sys_get_temp_dir(), 'coherence_stderr_');

        $cmd = sprintf(
            'docker exec -i jobsearch_worker sh -c %s < %s 2>%s',
            escapeshellarg('cd /app && python coherence.py'),
            escapeshellarg($tmpFile),
            escapeshellarg($stderrFile)
        );

        exec($cmd, $outputLines, $exitCode);
        $output = implode("\n", $outputLines);
        $stderr = trim((string) @file_get_contents($stderrFile));
        @unlink($tmpFile);
        @unlink($stderrFile);

        if ($exitCode !== 0 || $output === '') {
            $detail = $stderr !== '' ? $stderr : "sin salida (exit code {$exitCode})";
            Log::error("EvaluateVacancyCoherenceJob: worker sin output", ['detail' => $detail]);
            throw new \RuntimeException("EvaluateVacancyCoherenceJob: worker sin output. Detalle: {$detail}");
        }

        $data = json_decode($output, true);

        if (json_last_error() !== JSON_ERROR_NONE || !isset($data['results'])) {
            Log::error("EvaluateVacancyCoherenceJob: JSON inválido", ['output' => substr($output, 0, 200)]);
            return;
        }

        $flagged = 0;

        foreach ($data['results'] as $r) {
            $fields = [
                'vacante_coherente' => $r['vacante_coherente'],
                'coherence_detail'  => $r['coherence_detail'],
            ];

            if ($r['vacante_coherente'] === false) {
                $fields['status'] = VacancyStatus::NoIdoneo->value;
                $flagged++;
            }

            Vacancy::where('id', $r['id'])->update($fields);
        }

        Log::info("EvaluateVacancyCoherenceJob: completado", [
            'evaluadas'          => count($data['results']),
            'marcadas_no_idoneo' => $flagged,
        ]);
    }
}
