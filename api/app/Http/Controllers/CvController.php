<?php

namespace App\Http\Controllers;

use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class CvController extends Controller
{
    private string $cvPath = '/home/dev/projects/jobsearch/worker/data/cv.pdf';

    public function info(): JsonResponse
    {
        if (!file_exists($this->cvPath)) {
            return response()->json(['exists' => false]);
        }

        return response()->json([
            'exists'        => true,
            'size_kb'       => round(filesize($this->cvPath) / 1024, 1),
            'last_modified' => date('Y-m-d H:i:s', filemtime($this->cvPath)),
        ]);
    }

    public function upload(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'cv' => 'required|file|mimes:pdf|max:5120',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()->first()], 422);
        }

        $request->file('cv')->move(
            dirname($this->cvPath),
            basename($this->cvPath)
        );

        return response()->json([
            'ok'            => true,
            'size_kb'       => round(filesize($this->cvPath) / 1024, 1),
            'last_modified' => date('Y-m-d H:i:s', filemtime($this->cvPath)),
        ]);
    }
}