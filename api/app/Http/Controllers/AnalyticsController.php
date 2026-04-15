<?php

namespace App\Http\Controllers;

use App\Services\AnalyticsService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AnalyticsController extends Controller
{
    public function __construct(private readonly AnalyticsService $analyticsService) {}

    public function summary(Request $request): JsonResponse
    {
        return response()->json($this->analyticsService->summary($request->query('last_visit')));
    }

    public function skills(): JsonResponse
    {
        return response()->json($this->analyticsService->skills());
    }

    public function companies(): JsonResponse
    {
        return response()->json($this->analyticsService->companies());
    }

    public function salaries(): JsonResponse
    {
        return response()->json($this->analyticsService->salaries());
    }

    public function statusTimeline(): JsonResponse
    {
        return response()->json($this->analyticsService->statusTimeline());
    }
}