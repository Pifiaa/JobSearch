<?php

namespace App\Services;

use App\Models\Source;
use App\Models\Vacancy;
use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class VacancyPersistenceService
{
    public function persistMany(array $vacancies, Source $source): array
    {
        $created    = 0;
        $skipped    = 0;
        $createdIds = [];

        foreach ($vacancies as $data) {
            $id = $this->persistOne($data, $source);
            if ($id !== null) {
                $created++;
                $createdIds[] = $id;
            } else {
                $skipped++;
            }
        }

        Log::info("VacancyPersistenceService: persistencia completa", [
            'source'  => $source->name,
            'created' => $created,
            'skipped' => $skipped,
        ]);

        return compact('created', 'skipped', 'createdIds');
    }

    private function persistOne(array $data, Source $source): ?int
    {
        if ($this->isDuplicate($data, $source->id)) {
            return null;
        }

        $vacancy = Vacancy::create([
            'source_id'          => $source->id,
            'external_id'        => $data['external_id'],
            'title'              => $data['title'],
            'company'            => $data['company'] ?? null,
            'city'               => $data['city'] ?? null,
            'department'         => $data['department'] ?? null,
            'country'            => $data['country'] ?? null,
            'modality'           => $data['modality'] ?? null,
            'salary_range'       => $data['salary_range'] ?? null,
            'description'        => $data['description'] ?? null,
            'description_hash'   => $data['description_hash'] ?? null,
            'url'                => $data['url'],
            'published_at'       => $this->parseDate($data['published_at'] ?? null),
            'scraped_at'         => now(),
            'cv_score'           => $data['cv_score'] ?? null,
            'cv_score_semantic'  => $data['cv_score_semantic'] ?? null,
            'cv_keywords_detail' => $data['cv_keywords_detail'] ?? null,
        ]);

        return $vacancy->id;
    }

    private function parseDate(?string $date): ?Carbon
    {
        if (empty($date)) {
            return null;
        }

        foreach (['d/m/Y', 'Y-m-d', 'd-m-Y'] as $format) {
            try {
                return Carbon::createFromFormat($format, $date);
            } catch (\Exception) {
                continue;
            }
        }

        Log::warning("VacancyPersistenceService: fecha no reconocida", ['date' => $date]);
        return null;
    }

    private function isDuplicate(array $data, int $sourceId): bool
    {
        $byExternalId = Vacancy::where('source_id', $sourceId)
            ->where('external_id', $data['external_id'])
            ->where('is_active', true)
            ->whereNotIn('status', ['descartada', 'no_idoneo'])
            ->exists();

        if ($byExternalId) {
            return true;
        }

        if (!empty($data['description_hash'])) {
            return Vacancy::where('description_hash', $data['description_hash'])
                ->where('is_active', true)
                ->whereNotIn('status', ['descartada', 'no_idoneo'])
                ->exists();
        }

        return false;
    }
}