<?php

namespace App\Http\Controllers;

use App\Models\Vacancy;
use App\Services\CvTailorService;
use Illuminate\Http\JsonResponse;

class CvTailorController extends Controller
{
    public function __construct(private readonly CvTailorService $cvTailorService) {}

    public function generate(int $id): JsonResponse
    {
        $vacancy = Vacancy::where('is_active', true)->findOrFail($id);

        try {
            $data = $this->cvTailorService->tailor($vacancy);
        } catch (\RuntimeException $e) {
            return response()->json(['error' => $e->getMessage()], 422);
        }

        return response()->json(['tailored_cv' => $data]);
    }

    public function exportPdf(int $id)
    {
        $vacancy = Vacancy::where('is_active', true)->findOrFail($id);

        try {
            return $this->cvTailorService->exportPdf($vacancy);
        } catch (\RuntimeException $e) {
            return response()->json(['error' => $e->getMessage()], 422);
        }
    }

    public function exportBrief(int $id)
    {
        $vacancy = Vacancy::where('is_active', true)->findOrFail($id);

        try {
            return $this->cvTailorService->exportBrief($vacancy);
        } catch (\RuntimeException $e) {
            return response()->json(['error' => $e->getMessage()], 422);
        }
    }
}
