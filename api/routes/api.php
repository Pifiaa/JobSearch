<?php

use App\Http\Controllers\AnalyticsController;
use App\Http\Controllers\ScraperController;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\VacancyController;
use App\Http\Controllers\CompanyBlacklistController;
use App\Http\Controllers\CvController;

Route::get('/vacancies',               [VacancyController::class, 'index']);
Route::patch('/vacancies/{id}/status', [VacancyController::class, 'updateStatus']);
Route::get('/vacancies/{id}/status-history', [VacancyController::class, 'statusHistory']);

Route::post('/scraper/run/all', [ScraperController::class, 'runAll']);
Route::post('/scraper/run/{sourceId}', [ScraperController::class, 'run']);

Route::prefix('analytics')->controller(AnalyticsController::class)->group(function () {
    Route::get('summary',         'summary');
    Route::get('skills',          'skills');
    Route::get('companies',       'companies');
    Route::get('salaries',        'salaries');
    Route::get('status-timeline', 'statusTimeline');
});

Route::get('/cv/info',     [CvController::class, 'info']);
Route::post('/cv/upload',  [CvController::class, 'upload']);

Route::post('/companies/blacklist', [CompanyBlacklistController::class, 'store']);
