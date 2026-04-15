<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;

class AnalyticsService
{
    public function summary(?string $lastVisit = null): array
    {
        $total = DB::table('vacancies')->where('is_active', true)->count();

        $byModality = DB::table('vacancies')
            ->select('modality', DB::raw('COUNT(*) as total'))
            ->where('is_active', true)
            ->groupBy('modality')
            ->orderByDesc('total')
            ->get();

        $bySource = DB::table('vacancies')
            ->join('sources', 'vacancies.source_id', '=', 'sources.id')
            ->select('sources.name as source', DB::raw('COUNT(*) as total'))
            ->where('vacancies.is_active', true)
            ->groupBy('sources.name')
            ->orderByDesc('total')
            ->get();

        $newSince = null;
        if ($lastVisit) {
            try {
                $newSince = DB::table('vacancies')
                    ->where('is_active', true)
                    ->where('scraped_at', '>', $lastVisit)
                    ->count();
            } catch (\Throwable) {
                $newSince = null;
            }
        }

        return [
            'total'       => $total,
            'by_modality' => $byModality,
            'by_source'   => $bySource,
            'new_since'   => $newSince,
        ];
    }

    public function skills(int $limit = 30): array
    {
        $rows = DB::table('vacancies')
            ->select('cv_keywords_detail')
            ->where('is_active', true)
            ->whereNotNull('cv_keywords_detail')
            ->get();

        $counts = [];
        foreach ($rows as $row) {
            $detail = json_decode($row->cv_keywords_detail, true);
            $all = array_merge(
                $detail['matched'] ?? [],
                $detail['missing'] ?? []
            );
            foreach ($all as $kw) {
                $kw = strtolower(trim($kw));
                if ($kw === '') continue;
                $counts[$kw] = ($counts[$kw] ?? 0) + 1;
            }
        }

        arsort($counts);
        $top = array_slice($counts, 0, $limit, true);

        return array_map(
            fn($skill, $total) => ['skill' => $skill, 'total' => $total],
            array_keys($top),
            array_values($top)
        );
    }

    public function companies(int $limit = 20): array
    {
        return DB::table('vacancies')
            ->select('company', DB::raw('COUNT(*) as total'))
            ->where('is_active', true)
            ->whereNotNull('company')
            ->where('company', '!=', '')
            ->groupBy('company')
            ->orderByDesc('total')
            ->limit($limit)
            ->get()
            ->toArray();
    }

    public function salaries(): array
    {
        return DB::table('vacancies')
            ->select('modality', 'salary_range', DB::raw('COUNT(*) as total'))
            ->where('is_active', true)
            ->whereNotNull('salary_range')
            ->where('salary_range', '!=', '')
            ->groupBy('modality', 'salary_range')
            ->orderBy('modality')
            ->orderByDesc('total')
            ->get()
            ->toArray();
    }

    public function statusTimeline(): array
    {
        $byStatus = DB::table('vacancies')
            ->select('status', DB::raw('COUNT(*) as total'))
            ->where('is_active', true)
            ->groupBy('status')
            ->orderByDesc('total')
            ->get()
            ->toArray();

        $timeline = DB::table('vacancies')
            ->select(
                'status',
                DB::raw("DATE_TRUNC('day', status_changed_at) as date"),
                DB::raw('COUNT(*) as total')
            )
            ->where('is_active', true)
            ->whereNotNull('status_changed_at')
            ->where('status', '!=', 'nueva')
            ->groupBy('status', DB::raw("DATE_TRUNC('day', status_changed_at)"))
            ->orderBy('date')
            ->get()
            ->toArray();

        return [
            'by_status' => $byStatus,
            'timeline'  => $timeline,
        ];
    }
}