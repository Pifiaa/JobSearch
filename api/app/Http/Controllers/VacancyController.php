<?php
namespace App\Http\Controllers;
use App\Http\Requests\UpdateVacancyStatusRequest;
use App\Http\Requests\VacancyFilterRequest;
use App\Models\Vacancy;
use App\Services\VacancyService;
use Illuminate\Http\JsonResponse;

class VacancyController extends Controller
{
    public function __construct(private readonly VacancyService $vacancyService) {}

    public function index(VacancyFilterRequest $request): JsonResponse
    {
        $vacancies = $this->vacancyService->listFiltered($request);
        return response()->json($vacancies);
    }

    public function updateStatus(UpdateVacancyStatusRequest $request, int $id): JsonResponse
    {
        $vacancy = Vacancy::where('is_active', true)->findOrFail($id);
        $vacancy->update(['status' => $request->input('status')]);
        return response()->json($vacancy->fresh('source'));
    }
}