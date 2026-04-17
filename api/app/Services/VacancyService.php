<?php

namespace App\Services;

use App\Http\Requests\VacancyFilterRequest;
use App\Models\Vacancy;
use Illuminate\Pagination\LengthAwarePaginator;

class VacancyService
{
    public function listFiltered(VacancyFilterRequest $request): LengthAwarePaginator
    {
        $query = Vacancy::with('source')
            ->where('is_active', true);

        if ($request->filled('source_id')) {
            $query->where('source_id', $request->integer('source_id'));
        }

        if ($request->filled('modality')) {
            $query->where('modality', $request->input('modality'));
        }

        if ($request->filled('city')) {
            $query->whereRaw('LOWER(city) LIKE ?', ['%' . strtolower($request->input('city')) . '%']);
        }

        if ($request->filled('status')) {
            $query->where('status', $request->input('status'));
        }

        if ($request->filled('search')) {
            $term = '%' . strtolower($request->input('search')) . '%';
            $query->where(function ($q) use ($term) {
                $q->whereRaw('LOWER(title) LIKE ?', [$term])
                  ->orWhereRaw('LOWER(description) LIKE ?', [$term]);
            });
        }

        if ($request->filled('score_min')) {
            $scoreMin = $request->float('score_min');
            $query->whereNotNull('cv_score')
                ->whereNotNull('cv_score_semantic')
                ->whereRaw(
                    '(cv_score * 0.6 + cv_score_semantic * 0.4) >= ?',
                    [$scoreMin]
                );
        }

        match ($request->input('sort', 'recent')) {
            'score'   => $query->orderByRaw('(COALESCE(cv_score, 0) * 0.6 + COALESCE(cv_score_semantic, 0) * 0.4) DESC'),
            'company' => $query->orderBy('company'),
            default   => $query->orderByRaw("CASE WHEN status IN ('descartada', 'no_idoneo') THEN 1 ELSE 0 END ASC, scraped_at DESC"),
        };

        return $query->paginate($request->integer('per_page', 20));
    }
}