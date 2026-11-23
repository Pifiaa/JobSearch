<?php
namespace App\Jobs;
use App\Enums\VacancyStatus;
use App\Models\Vacancy;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Log;

class RescoreVacanciesJob implements ShouldQueue
{
    use Queueable;

    public int $timeout = 3600;
    public int $tries   = 1;

    public function handle(): void
    {
        Log::info("RescoreVacanciesJob: iniciando");

        $vacancies = Vacancy::whereNotIn('status', [VacancyStatus::Descartada->value])
            ->whereNotNull('description')
            ->get(['id', 'description']);

        if ($vacancies->isEmpty()) {
            Log::info("RescoreVacanciesJob: sin vacantes para re-scorear");
            return;
        }

        Log::info("RescoreVacanciesJob: re-scoreando", ['total' => $vacancies->count()]);

        $input   = json_encode($vacancies->toArray());
        $tmpFile = tempnam(sys_get_temp_dir(), 'rescore_') . '.json';
        file_put_contents($tmpFile, $input);

        $cmd = sprintf(
            'docker exec -i jobsearch_worker sh -c %s < %s 2>/dev/null',
            escapeshellarg('cd /app && python rescorer.py'),
            escapeshellarg($tmpFile)
        );

        $output = shell_exec($cmd);
        unlink($tmpFile);

        if (!$output) {
            Log::error("RescoreVacanciesJob: worker sin output");
            return;
        }

        $data = json_decode($output, true);

        if (json_last_error() !== JSON_ERROR_NONE || !isset($data['results'])) {
            Log::error("RescoreVacanciesJob: JSON inválido", ['output' => substr($output, 0, 200)]);
            return;
        }

        $updated   = 0;
        $discarded = 0;

        foreach ($data['results'] as $r) {
            $combined = $r['cv_score'] * 0.6 + $r['cv_score_semantic'] * 0.4;

            $fields = [
                'cv_score'           => $r['cv_score'],
                'cv_score_semantic'  => $r['cv_score_semantic'],
                'cv_keywords_detail' => $r['cv_keywords_detail'],
                'llm_score'          => $r['llm_score'] ?? null,
                'llm_detail'         => $r['llm_detail'] ?? null,
            ];

            if ($combined < 1.0) {
                $fields['status'] = VacancyStatus::Descartada->value;
                $discarded++;
            }

            Vacancy::where('id', $r['id'])->update($fields);
            $updated++;
        }

        Log::info("RescoreVacanciesJob: completado", [
            'updated'   => $updated,
            'discarded' => $discarded,
        ]);
    }
}