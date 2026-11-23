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
        $created     = 0;
        $reactivated = 0;
        $skipped     = 0;
        $createdIds  = [];

        foreach ($vacancies as $data) {
            $result = $this->persistOne($data, $source);
            if ($result === null) {
                $skipped++;
                continue;
            }

            $createdIds[] = $result['id'];
            if ($result['reactivated']) {
                $reactivated++;
            } else {
                $created++;
            }
        }

        Log::info("VacancyPersistenceService: persistencia completa", [
            'source'      => $source->name,
            'created'     => $created,
            'reactivated' => $reactivated,
            'skipped'     => $skipped,
        ]);

        return compact('created', 'reactivated', 'skipped', 'createdIds');
    }

    /**
     * @return array{id: int, reactivated: bool}|null
     */
    private function persistOne(array $data, Source $source): ?array
    {
        if ($this->isDuplicate($data, $source->id)) {
            return null;
        }

        // Si esta misma vacante (source_id + external_id) existe pero está
        // inactiva, la única forma en que llegó a is_active=false es que
        // vacancies:clean-old la desactivó por inactividad (es el único
        // lugar del código que lo hace, y solo sobre status='nueva'; nunca
        // se toca al descartar una vacante manualmente). Si reaparece en un
        // scrape, hay que reactivarla en vez de intentar un INSERT que va a
        // chocar contra el índice único (source_id, external_id) y perderse
        // en silencio como "duplicate key ignorado".
        $inactive = Vacancy::where('source_id', $source->id)
            ->where('external_id', $data['external_id'])
            ->where('is_active', false)
            ->first();

        if ($inactive !== null) {
            $inactive->update([
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
                'is_active'          => true,
            ]);

            return ['id' => $inactive->id, 'reactivated' => true];
        }

        try {
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

            return ['id' => $vacancy->id, 'reactivated' => false];
        } catch (\Illuminate\Database\UniqueConstraintViolationException $e) {
            Log::warning("VacancyPersistenceService: duplicate key ignorado", [
                'source'      => $source->name,
                'external_id' => $data['external_id'] ?? null,
            ]);
            return null;
        }
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