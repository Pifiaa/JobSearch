<?php
namespace App\Console\Commands;

use App\Enums\VacancyStatus;
use App\Models\Vacancy;
use Illuminate\Console\Command;

class DiscardLowScoreVacancies extends Command
{
    protected $signature   = 'vacancies:discard-low-score {--threshold=1.0 : Score combinado mínimo}';
    protected $description = 'Marca como descartada las vacantes con score combinado menor al threshold';

    public function handle(): int
    {
        $threshold = (float) $this->option('threshold');

        $affected = Vacancy::whereNotIn('status', [VacancyStatus::Descartada->value])
            ->whereNotNull('cv_score')
            ->whereNotNull('cv_score_semantic')
            ->whereRaw('(cv_score::float * 0.6 + cv_score_semantic * 0.4) < ?', [$threshold])
            ->update(['status' => VacancyStatus::Descartada]);

        $this->info("Vacantes marcadas como descartada: {$affected}");
        return Command::SUCCESS;
    }
}