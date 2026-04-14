<?php

use App\Http\Controllers\ScraperController;
use Illuminate\Support\Facades\Route;

Route::post('/scraper/run/all', [ScraperController::class, 'runAll']);
Route::post('/scraper/run/{sourceId}', [ScraperController::class, 'run']);