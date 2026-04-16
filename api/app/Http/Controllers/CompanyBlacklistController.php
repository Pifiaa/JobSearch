<?php

namespace App\Http\Controllers;

use App\Models\CompanyBlacklist;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CompanyBlacklistController extends Controller
{
    public function store(Request $request): JsonResponse
    {
        $request->validate([
            'name'   => 'required|string|max:255',
            'reason' => 'nullable|string|max:500',
        ]);

        $entry = CompanyBlacklist::firstOrCreate(
            ['name' => $request->input('name')],
            ['reason' => $request->input('reason')]
        );

        return response()->json($entry, $entry->wasRecentlyCreated ? 201 : 200);
    }
}